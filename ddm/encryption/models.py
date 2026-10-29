from __future__ import annotations

import base64
import contextlib
import json
from io import BytesIO
from struct import pack
from typing import TYPE_CHECKING, Any

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import HMAC, SHA256
from Crypto.Protocol.KDF import HKDF
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from django.db import models
from django.views.decorators.debug import sensitive_variables

# Fixed, hardcoded domain-separation context for wrapping a per-project
# private key with a SECRET_KEY-derived key (see wrap_private_key()/
# unwrap_private_key()). Not secret, never needs to change - it just keeps
# this derivation distinct from any other use of HKDF on SECRET_KEY.
_PRIVATE_KEY_WRAP_CONTEXT = b"ddm:donationproject:private-key-wrap:v1"

if TYPE_CHECKING:
    from Crypto.PublicKey.RSA import RsaKey

    from ddm.projects.models import DonationProject


class ModelWithEncryptedData(models.Model):
    project: DonationProject

    class Meta:
        abstract = True

    @sensitive_variables()
    def save(self, *args, **kwargs) -> None:

        if "encryptor" in kwargs:
            encryptor = kwargs.pop("encryptor")
        else:
            secret = kwargs.get("secret", self.project.secret_key)
            encryptor = Encryption(
                secret, self.project.get_salt(), self.project.public_key
            )

        # Prevent double encryption.
        with contextlib.suppress(TypeError):
            self.data = encryptor.encrypt(self.data)

        super().save(*args, **kwargs)

    @sensitive_variables()
    def get_decrypted_data(
        self, secret: str, salt: str, decryptor: Decryption | None = None
    ) -> Any:  # noqa: ANN401
        # `salt` is kept in the signature for backward compatibility with
        # existing callers, but is no longer used here: get_decryptor()
        # resolves it internally (via self.project.get_salt()) whenever the
        # legacy on-the-fly derivation path is actually taken.
        try:
            if decryptor:
                return decryptor.decrypt(self.data)
            return self.project.get_decryptor(secret=secret).decrypt(self.data)
        except ValueError as e:
            msg = "Wrong secret"
            raise ValueError(msg) from e


class PRNG:
    def __init__(self, seed: Any) -> None:  # noqa: ANN401
        self.index = 0
        self.seed = seed
        self.buffer = b""

    def __call__(self, n: int) -> bytes:
        while len(self.buffer) < n:
            self.buffer += HMAC.new(self.seed + pack("<I", self.index)).digest()
            self.index += 1
        result, self.buffer = self.buffer[:n], self.buffer[n:]
        return result


class AsyncSyncCrypto:
    @staticmethod
    def get_public_key(secret: str, salt: str) -> bytes:
        return Encryption.get_rsa(secret, salt).publickey().exportKey()

    @staticmethod
    def get_rsa(secret: str, salt: str) -> RsaKey:
        if secret is None:
            msg = "secret is None."
            raise ValueError(msg)
        if salt is None:
            msg = "salt is None."
            raise ValueError(msg)
        seed_128 = HMAC.new(bytes(secret, "utf-8") + bytes(salt, "utf-8")).digest()
        return RSA.generate(2048, randfunc=PRNG(seed_128))


@sensitive_variables()
def _derive_wrap_key(secret: str) -> bytes:
    """
    Derives a 256-bit AES key from `secret` (always settings.SECRET_KEY in
    practice) via HKDF, for wrapping/unwrapping a DonationProject's own
    randomly-generated RSA private key (see wrap_private_key()/
    unwrap_private_key()). No per-call salt: `secret` is already a single,
    high-entropy value with exactly one derivation purpose here, so the
    fixed `context` alone gives sufficient domain separation. Note this
    means one shared wrap key is derived once per process and reused across
    every project - safe only because each wrap below uses a fresh random
    AES-EAX nonce; do not change this to a deterministic nonce.
    """
    return HKDF(
        bytes(secret, "utf-8"), 32, b"", SHA256, context=_PRIVATE_KEY_WRAP_CONTEXT
    )


@sensitive_variables()
def wrap_private_key(secret: str, private_key_der: bytes) -> bytes:
    """Encrypts a DER-encoded RSA private key for storage at rest."""
    wrap_key = _derive_wrap_key(secret)
    cipher = AES.new(wrap_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(private_key_der)
    return cipher.nonce + tag + ciphertext


@sensitive_variables()
def unwrap_private_key(secret: str, wrapped: bytes) -> bytes:
    """
    Reverses wrap_private_key(). Raises ValueError if `secret` is wrong or
    `wrapped` was tampered with (AES-EAX tag verification failure).
    """
    wrap_key = _derive_wrap_key(secret)
    nonce, tag, ciphertext = wrapped[:16], wrapped[16:32], wrapped[32:]
    cipher = AES.new(wrap_key, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


class Encryption(AsyncSyncCrypto):
    def __init__(
        self,
        secret: str | None = None,
        salt: str | None = None,
        public: str | None = None,
    ) -> None:
        if public:
            self.public_key = public
        else:
            self.public_key = self.get_public_key(secret, salt)

    def encrypt(self, value: Any) -> bytes:  # noqa: ANN401
        """
        Save encrypted data to the database, either use a supplied 'public_key'
        or generate the material dynamically.
        """
        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        cipher_data, tag = cipher_aes.encrypt_and_digest(
            bytes(json.dumps(value), "utf-8")
        )
        cipher_rsa = PKCS1_OAEP.new(RSA.importKey(self.public_key))
        encrypted_session_key = cipher_rsa.encrypt(session_key)
        payload = encrypted_session_key + cipher_aes.nonce + tag + cipher_data
        return base64.encodebytes(payload)


class Decryption(AsyncSyncCrypto):
    def __init__(
        self,
        secret: str | None = None,
        salt: str | None = None,
        private_key: bytes | None = None,
    ) -> None:
        if private_key is not None:
            self.rsa = RSA.import_key(private_key)
        else:
            self.rsa = self.get_rsa(secret, salt)

    def decrypt(self, value: Any) -> Any:  # noqa: ANN401
        """Fetch encrypted data from the database and decode it.

        Raises ValueError if decryption fails.
        """
        value_bytes = BytesIO(base64.decodebytes(value))
        encrypted_session_key = value_bytes.read(self.rsa.size_in_bytes())
        nonce = value_bytes.read(16)
        tag = value_bytes.read(16)
        cipher_data = value_bytes.read()
        session_key = PKCS1_OAEP.new(self.rsa).decrypt(encrypted_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted = cipher_aes.decrypt_and_verify(cipher_data, tag)
        return json.loads(decrypted.decode("utf-8"))
