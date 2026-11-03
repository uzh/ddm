# Settings Reference
 
This page lists the settings that configure DDM in your project's `settings.py`:
 
- [DDM Settings](#ddm-settings): DDM's own settings. All are optional.
- [Django and Third-Party Settings](#django-and-third-party-settings): Settings of Django and
  the packages DDM uses, with the values DDM needs.

Researchers configure per-project options, such as branding, in the researcher interface; see
[For Researchers](../researchers/index.md).
 
## DDM Settings
 
### `DDM_SETTINGS`
 
A dictionary of DDM's own settings. All keys are optional; if you omit the dictionary, DDM
uses the defaults.
 
| Key                           | Default                  | Description                                                                                                                                                                                                                                 |
|-------------------------------|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `EMAIL_PERMISSION_CHECK`      | Not set (no restriction) | Regular expression. Only users whose email matches get researcher access. Superusers and users with **Ignore email restriction** enabled always get access. See [User Authentication](configuration/user_authentication.md#access-control). |
| `MAX_DONATION_UPLOAD_SIZE`    | `104857600` (100 MB)     | Maximum size in bytes of the uncompressed `data_donation.json` in a participant's upload. Larger uploads are rejected and logged.                                                                                                           |
| `PROJECT_API_THROTTLE_RATE`   | `'100/min'`              | Rate limit per access token for the project API. See [Security → Rate Limiting](security.md#rate-limiting).                                                                                                                                 |
| `EXCEPTION_LOG_THROTTLE_RATE` | `'20/min'`               | Rate limit per IP address for the public client-side exception log. See [Security → Rate Limiting](security.md#rate-limiting).                                                                                                              |
 
Rate limits use the format `'<number>/<period>'`, where the period is `s`, `min`, `h`, or `d`
(for example, `'200/min'`).
 
```python
# settings.py
 
DDM_SETTINGS = {
    'EMAIL_PERMISSION_CHECK': r'.*(\.|@)somedomain\.com$',
    'MAX_DONATION_UPLOAD_SIZE': 100 * 1024 * 1024,
    'PROJECT_API_THROTTLE_RATE': '100/min',
    'EXCEPTION_LOG_THROTTLE_RATE': '20/min',
}
```
 
### Header Images
 
Default images for the header of the participant-facing pages. Researchers can replace them
per project.
 
| Setting                        | Default         | Description                                       |
|--------------------------------|-----------------|---------------------------------------------------|
| `DDM_DEFAULT_HEADER_IMG_LEFT`  | `''` (no image) | URL of the image on the left side of the header.  |
| `DDM_DEFAULT_HEADER_IMG_RIGHT` | `''` (no image) | URL of the image on the right side of the header. |
 
Use a URL the browser can load: either a full URL or a path your server serves, such as a
file under `STATIC_URL`.
 
```python
# settings.py
 
DDM_DEFAULT_HEADER_IMG_LEFT = '/static/images/logo_left.png'
DDM_DEFAULT_HEADER_IMG_RIGHT = 'https://example.org/logo_right.png'
```
 
## Django and Third-Party Settings
 
These settings belong to Django or to packages DDM depends on. The tables list only the
settings that matter for DDM, with the values DDM needs or recommends. The
[Installation Guide](installation.md#update-settingspy) shows how to set them.
 
### Django
 
| Setting               | Value for DDM                               | Description                                                                                                                                                                                                      |
|-----------------------|---------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `SECRET_KEY`          | Required; keep secret and back it up        | Part of the encryption key for donated data in standard projects. Losing or changing it makes that data unreadable. See [Security → Secret Key & Encryption at Rest](security.md#secret-key-encryption-at-rest). |
| `USE_TZ`              | `True` (required)                           | Enables time zone support. New projects set this by default.                                                                                                                                                     |
| `STATIC_ROOT`         | Required, for example `BASE_DIR / 'static'` | Where `collectstatic` puts static files, including DDM's frontend bundles.                                                                                                                                       |
| `MEDIA_ROOT`          | Required, for example `BASE_DIR / 'media'`  | Where files uploaded through CKEditor are stored.                                                                                                                                                                |
| `MEDIA_URL`           | Required, for example `'/media/'`           | URL that uploaded files are served from.                                                                                                                                                                         |
| `LOGIN_REDIRECT_URL`  | Recommended: `'/ddm/projects/'`             | Where users go after logging in. Django's default, `'/accounts/profile/'`, doesn't exist in DDM.                                                                                                                 |
| `LOGOUT_REDIRECT_URL` | Recommended: `'/login/'`                    | Where users go after logging out. Django's default is `None`.                                                                                                                                                    |
 
For login views and OIDC setup, see [User Authentication](configuration/user_authentication.md).
 
### CKEditor
 
Settings of [django-ckeditor-5](https://github.com/hvlads/django-ckeditor-5), the rich text
editor that DDM uses. See
[Security → CKEditor File Upload Security](security.md#ckeditor-file-upload-security) before
you change the upload settings.
 
| Setting                             | Default                                                          | Description                                                                                                                                                                              |
|-------------------------------------|------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `CKEDITOR_5_CONFIGS`                | DDM's `ddm_ckeditor` and `ddm_ckeditor_temp_func` configurations | Editor configurations. If you define `ddm_ckeditor` or `ddm_ckeditor_temp_func`, your version replaces DDM's. See [CKEditor Configuration](configuration/customize_ckeditor_configs.md). |
| `CKEDITOR_5_FILE_UPLOAD_PERMISSION` | `'staff'`                                                        | Who can upload files. Set it to `'authenticated'` so researchers who aren't staff can upload.                                                                                            |
| `CKEDITOR_5_ALLOW_ALL_FILE_TYPES`   | `False`                                                          | If `False`, only images are accepted, and their content is validated. If `True`, only the extension is checked.                                                                          |
| `CKEDITOR_5_UPLOAD_FILE_TYPES`      | `['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']`           | Allowed file extensions if `CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True`.                                                                                                                     |
| `CKEDITOR_5_MAX_FILE_SIZE`          | `0` (unlimited)                                                  | Maximum upload size in MB. Always set a limit.                                                                                                                                           |
 
### webpack-loader
 
| Setting          | Value for DDM                                                                                     | Description                                                                                                                                                           |
|------------------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `WEBPACK_LOADER` | Required; copy the configuration from the [Installation Guide](installation.md#update-settingspy) | Points [django-webpack-loader](https://github.com/django-webpack/django-webpack-loader) to DDM's pre-built frontend bundles (`DDM_UPLOADER` and `DDM_QUESTIONNAIRE`). |
