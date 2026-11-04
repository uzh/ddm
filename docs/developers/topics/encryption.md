# Data Encryption

This page describes the encryption DDM implements itself, and the encryption a site
hosting DDM is responsible for setting up around it.

## Encryption in transit and at rest

### Encryption in transit

Setting up transport encryption (TLS/HTTPS for all traffic between clients and the server) is the
hosting site's responsibility — see the
[Django deployment checklist](https://docs.djangoproject.com/en/5.2/topics/security/#ssl-https)
for pointers. DDM minimizes how much donated data ever has to travel over the network in the
first place by doing extraction and filtering client-side, in the participant's browser, before
anything is submitted. The connection between the application server and the database should
also be secured, and the database itself should live on an encrypted disk.

### Encryption at rest

DDM encrypts all donated data at the field level before it is written to the database. Two
models hold encrypted data — `DataDonation` and `QuestionnaireResponse` (both inherit from
`ModelWithEncryptedData`, `ddm/encryption/models.py`) — and both encrypt/decrypt through their
owning `DonationProject`.

Each `DonationProject` has its own RSA keypair. The public key is used to encrypt data on write;
the private key is needed to decrypt it. How that keypair is obtained depends on the project:

- **Standard projects** (`super_secret=False`, the default): on first save, DDM generates a
  genuinely random RSA-2048 keypair (`RSA.generate(2048)`, no seed). The public key is stored
  as-is in `DonationProject.public_key`; the private key is wrapped at rest (see below) using a
  key derived from `settings.SECRET_KEY`, and the wrapped bytes are stored in
  `DonationProject.wrapped_private_key`. Decryption unwraps this field with `SECRET_KEY` — nothing
  needs to be re-derived or remembered per project.
- **Enhanced-encryption ("super secret") projects** (`super_secret=True`, the "Enable enhanced
  encryption" checkbox researchers see at project creation,
  `ddm/projects/templates/ddm_projects/form_sections/_enhanced_encryption_block.html`): the
  keypair is *never stored*. Instead it is deterministically re-derived on every use from a
  **project-specific passphrase** (held only in memory, via the `DonationProject.secret`/
  `secret_key` property — never persisted to the database) and the project's `salt`. Losing the
  passphrase means the data can never be decrypted again, by design. Because the passphrase isn't
  in the database, it also can't be used server-side to template donated data into follow-up
  questionnaire questions (`get_decrypted_data` needs the real passphrase, not `SECRET_KEY`).
- **Legacy projects**: any standard project created *before* `wrapped_private_key` existed falls
  back to the same on-the-fly derivation as enhanced-encryption projects, keyed on
  `settings.SECRET_KEY` instead of a per-project passphrase. This keeps already-encrypted data
  for those projects decryptable without a backfill migration.

All three cases share one `salt` per project: `DonationProject.get_salt()` simply returns
`str(self.date_created)` — the project's creation timestamp, not an independently generated
random value. `date_created` must not be changed after creation, or the legacy/enhanced
derivation paths stop reproducing the original keypair.

!!! danger "`SECRET_KEY` is part of your encryption key material"

    For every standard project, `settings.SECRET_KEY` is what the private key is wrapped with.
    Losing `SECRET_KEY` (and not having a backup) makes every standard project's donated data
    permanently undecryptable; leaking it, combined with database access, lets an attacker
    decrypt everything. Treat it accordingly — see
    [Administrators → Security](../../administrators/security.md).

The branching logic above lives in `DonationProject.get_decryptor()`
(`ddm/projects/models.py`); `_generate_and_store_keypair()` is only ever called once, from
`save()`'s "no `public_key` yet" branch.

## Encryption and decryption process

DDM uses hybrid asymmetric/symmetric encryption for the data itself (RSA key sizes alone can't
hold more than a small amount of data, so each payload is encrypted symmetrically and only the
symmetric key is wrapped asymmetrically). This part of the scheme — implemented in the
`Encryption`/`Decryption` classes in `ddm/encryption/models.py` — is unchanged by the private-key
storage change described above; what changed is only where the private key used in step 2 of
decryption comes from.

**Encrypting a value** (`Encryption.encrypt()`):

1. Generate a random 128-bit AES session key, unique to this one value.
2. Encrypt the value symmetrically with that session key, using AES in EAX mode (authenticated
   encryption — this also produces a verification tag).
3. Encrypt the session key asymmetrically with the project's RSA public key, using
   [PKCS#1 OAEP](https://tools.ietf.org/html/rfc8017) padding.
4. Concatenate `encrypted_session_key + nonce + tag + ciphertext`, base64-encode it, and store
   that as the field's value.

**Decrypting a value** (`Decryption.decrypt()`):

1. Obtain the project's RSA private key — via `get_decryptor()`'s three-way branch described
   above.
2. Split the stored, base64-decoded payload back into `encrypted_session_key`, `nonce`, `tag`,
   and `ciphertext`.
3. Decrypt the session key asymmetrically with the private key (PKCS#1 OAEP).
4. Decrypt the ciphertext symmetrically with the session key (AES-EAX), verifying the tag.

### Deriving a keypair from a passphrase (enhanced-encryption and legacy projects)

When a keypair must be re-derived from a passphrase rather than read from storage
(`AsyncSyncCrypto.get_rsa()`):

1. Compute a 128-bit [HMAC](https://en.wikipedia.org/wiki/HMAC) digest of
   `passphrase + salt` (no hash function parameter is passed to pycryptodome's `HMAC.new()`,
   so it defaults to MD5 — this is used purely as a seed, not for its cryptographic properties).
2. Use that digest to seed a custom deterministic PRNG (`PRNG` in `ddm/encryption/models.py`,
   itself built from repeated HMAC calls over an incrementing counter).
3. Generate the RSA-2048 keypair using that PRNG as the randomness source
   (`RSA.generate(2048, randfunc=PRNG(seed))`) — the same seed always yields the same keypair.

The public key is exported and stored normally; the private key is never persisted for these
projects and must be re-derived the same way on every decryption.

### Wrapping a standard project's private key

For a standard project, the randomly generated private key is protected at rest with a second,
independent layer of AES-EAX encryption (`wrap_private_key()`/`unwrap_private_key()` and
`_derive_wrap_key()` in `ddm/encryption/models.py`):

1. Derive a 256-bit AES key from `settings.SECRET_KEY` via
   [HKDF](https://en.wikipedia.org/wiki/HKDF)-SHA256, using a fixed, non-secret
   domain-separation context string (`b"ddm:donationproject:private-key-wrap:v1"`) — this key is
   the same for every project on a given deployment, since it depends only on `SECRET_KEY`.
2. Encrypt the DER-encoded private key with AES-EAX, using a fresh random nonce for this project
   (never a deterministic one — that would make the per-project wrap key reuse unsafe).
3. Store `nonce + tag + ciphertext` in `DonationProject.wrapped_private_key`.

Unwrapping reverses this and raises `ValueError` if `SECRET_KEY` is wrong or the stored bytes
were tampered with (the AES-EAX tag won't verify).
