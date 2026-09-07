# Security Notices

## CKEditor File Upload Security

DDM uses [django-ckeditor-5](https://github.com/hvlads/django-ckeditor-5) for rich text editing.
File uploads are controlled by these Django settings:

* `CKEDITOR_5_FILE_UPLOAD_PERMISSION`
* `CKEDITOR_5_ALLOW_ALL_FILE_TYPES`
* `CKEDITOR_5_UPLOAD_FILE_TYPES`

### Default Behavior

With `CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False`, only images are allowed and file contents are validated.

### Risk: Allowing All File Types

Setting `CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True` validates **only file extensions**, not content. This creates vulnerabilities:

* Malicious files can use trusted extensions (e.g., `malware.pdf`)
* Polyglot files can bypass extension checks
* PDFs may contain JavaScript or exploits

### Mitigations

If your DDM instance allows registration by untrusted users, consider these protections:

| Mitigation | Implementation |
|---|---|
| Restrict file types | Limit the upload to images with `CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False` if PDFs aren't required |
| Validate content | Check magic bytes to verify file content matches the claimed type |
| Set secure headers | Serve uploads with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff` |
| Isolate domains | Serve uploads from a separate domain to protect session cookies |
| Sanitize PDFs | If PDFs are necessary, strip JavaScript and embedded content using a sanitization library |

## Content Security Policy

The participant-facing frontend (data donation upload and questionnaire) ships as two
precompiled Vue single-page apps, embedded via
[django-webpack-loader](https://github.com/django-webpack/django-webpack-loader). Both
work under a strict CSP with no exceptions needed in either `script-src` or `style-src`
(e.g. `default-src 'self'; script-src 'self'; style-src 'self'`).

To try this yourself: the test project has a `DDM_STRICT_CSP=1` environment variable
(see `test_project/settings.py`) that serves every page with this exact policy via
[django-csp](https://github.com/mozilla/django-csp), so you can click through the
participant flow locally and confirm nothing breaks.

## Django REST Framework Configuration

The API endpoints integrated in DDM use the [Django REST Framework](https://www.django-rest-framework.org) (DRF)

### Throttling of API Endpoints

The API endpoints integrated in DDM use DRF's default settings for throttling.
Therefore, you should configure the throttling settings so that they work best for your setup
([see the DRF documentation](https://www.django-rest-framework.org/api-guide/throttling/#userratethrottle))
