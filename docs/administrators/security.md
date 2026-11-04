# Security
 
This page covers the security considerations that are specific to DDM. For general Django
hardening, see [Installation Guide → Prepare for Production](installation.md#prepare-for-production).
 
## Checklist
 
- Back up `SECRET_KEY` and keep it out of version control.
  See [Secret Key & Encryption at Rest](#secret-key-encryption-at-rest).
- Restrict researcher access with `EMAIL_PERMISSION_CHECK`.
  See [Access & Login](#access-login).
- If you use local password login, throttle login attempts.
  See [Access & Login](#access-login).
- Set an upload size limit and review the allowed file types.
  See [File Uploads](#ckeditor-file-upload-security).
- Set a Content Security Policy.
  See [Content Security Policy](#content-security-policy).

## Secret Key & Encryption at Rest
 
In DDM, `SECRET_KEY` is part of the encryption key for donated data. DDM uses it to derive the
key that protects each project's private key (see
[Developers → Encryption](../developers/topics/encryption.md) for details). This applies to all
standard projects; projects with enhanced encryption are not affected (see below).
 
This has two consequences:
 
- **If you lose `SECRET_KEY`, you lose the data.** Without it, donated data in standard
  projects can't be decrypted. Changing `SECRET_KEY` has the same effect: DDM has no way to
  re-encrypt existing projects with a new key. Back up `SECRET_KEY` as carefully as your
  database.
- **If `SECRET_KEY` leaks, the data is exposed.** Anyone with `SECRET_KEY` and access to your
  database can decrypt all donated data in standard projects. Keep it out of version control,
  load it from an environment variable or a secrets manager, and don't reuse it across
  deployments.

**Enhanced encryption.** Projects with enhanced encryption derive their key from a
project-specific passphrase that DDM never stores. `SECRET_KEY` doesn't affect them.

### If Your Secret Key Leaks
 
1. Export the donated data of all standard projects. After the next step, DDM can no longer
   decrypt it.
2. Generate a new `SECRET_KEY` and deploy it.
3. Back up the new key.

## Access & Login
 
**Restrict researcher access.** Any logged-in user whose email matches
`DDM_SETTINGS['EMAIL_PERMISSION_CHECK']` gets researcher access. If the setting isn't defined,
every logged-in user does, including everyone your OIDC provider authenticates. See
[User Authentication → Access Control](configuration/user_authentication.md#access-control).
 
**Throttle login attempts.** Django's login view has no brute-force protection. If you keep
local password login (instead of only
[OIDC login](configuration/user_authentication.md#set-up-oidc-login)), add throttling
yourself, for example with [django-axes](https://github.com/jazzband/django-axes).
 
**Multi-factor authentication.** DDM doesn't provide MFA for local password login. To require
it, enforce it at your OIDC provider (recommended) or add a third-party Django MFA package.
 
## CKEditor File Upload Security
 
Researchers can upload files in the rich text editor. These settings control uploads (see
[Settings Reference](settings_reference.md) for defaults):
 
- `CKEDITOR_5_FILE_UPLOAD_PERMISSION`
- `CKEDITOR_5_ALLOW_ALL_FILE_TYPES`
- `CKEDITOR_5_UPLOAD_FILE_TYPES`
- `CKEDITOR_5_MAX_FILE_SIZE`

With `CKEDITOR_5_FILE_UPLOAD_PERMISSION = 'authenticated'`, every logged-in user can upload
files, not only users with researcher access. Control who can log in, for example through your
OIDC provider.
 
### Risk: Allowing All File Types
 
By default (`CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False`), only images can be uploaded, and their
content is validated.
 
With `CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True`, only the file extension is checked, not the
content. As a result:
 
- Malicious files can use an allowed extension (for example, `malware.pdf`).
- Polyglot files (valid as two file types at once) can pass the extension check.
- PDFs can contain JavaScript or exploits.

### Mitigations
 
Always set an upload size limit. `CKEDITOR_5_MAX_FILE_SIZE` defaults to `0` (unlimited), so
any logged-in user can fill your disk:
 
```python
# settings.py
 
CKEDITOR_5_MAX_FILE_SIZE = 10  # In MB.
```
 
If users you don't fully trust can log in, also consider:
 
| Mitigation          | How                                                                                         |
|---------------------|---------------------------------------------------------------------------------------------|
| Restrict file types | If you don't need PDFs, keep `CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False`.                     |
| Sanitize PDFs       | If you need PDFs, strip JavaScript and embedded content with a sanitization library.        |
| Validate content    | Check each file's magic bytes to confirm that its content matches its extension.            |
| Set secure headers  | Serve uploads with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`. |
| Isolate domains     | Serve uploads from a separate domain so that uploaded files can't access session cookies.   |
 
## Content Security Policy
 
All DDM pages work under a strict Content Security Policy (CSP) without exceptions, for
example:
 
```text
default-src 'self'; script-src 'self'; style-src 'self'
```
 
To set a CSP on your deployment, use [django-csp](https://github.com/mozilla/django-csp) or
your web server.
 
## Rate Limiting
 
DDM limits the request rate on the two endpoints that clients can reach without a researcher
login. For the settings and their format, see [Settings Reference](settings_reference.md).
 
| Endpoint                                                                                                         | Default limit                     |
|------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| Project API (token-authenticated; see [Researchers → APIs](../researchers/topics/apis.md))                       | 100 requests/minute per token     |
| Client-side exception log (public; see [Researchers → Project Logs](../researchers/data_center/project_logs.md)) | 20 requests/minute per IP address |
 
Researchers who are logged in to the researcher interface aren't rate-limited.
