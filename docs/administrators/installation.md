# Installation Guide
 
DDM is a [Django](https://www.djangoproject.com/) app. To run it, you need Python 3.12 or
newer ([download](https://www.python.org/downloads/)) and a Django 5.2 project to install
DDM into. This guide walks you through creating that project and adding DDM to it:
 
1. [Create a Django project](#create-a-django-project).
2. [Configure the database](#configure-the-database).
3. [Install DDM](#install-ddm) and configure your project for it.
4. [Set up the database tables](#set-up-the-database-tables).
5. [Test the installation](#test-the-installation).
6. [Prepare for production](#prepare-for-production).

For a production deployment (for example, with PostgreSQL, Nginx, and Gunicorn), follow a
comprehensive guide such as
[How To Set Up Django with Postgres, Nginx, and Gunicorn](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04)
alongside this one.
 
## Create a Django Project
 
Create a virtual environment and install Django into it. The commands below use `venv` and
`pip` on Linux or macOS. For Windows, see the
[Python venv documentation](https://docs.python.org/3/library/venv.html).
 
```bash
python -m venv /path/to/venv
source /path/to/venv/bin/activate
pip install "Django>=5.2,<6"
```
 
!!! tip "Using uv instead"
 
    [uv](https://docs.astral.sh/uv/) is faster and manages the virtual environment for you:
 
    ```bash
        uv init --app
        uv add "Django>=5.2,<6"
    ```
 
    For the rest of this guide, prefix commands with `uv run` instead of activating the
    environment (for example, `uv run django-admin startproject yourproject` or
    `uv run python manage.py migrate`), and install DDM with `uv add django-ddm` instead of
    `pip install django-ddm`.
 
Create a new project and change into its folder:
 
```bash
django-admin startproject yourproject
cd yourproject
```
 
The `yourproject` folder contains `manage.py` and a subfolder, also named `yourproject`, that
holds `settings.py` and `urls.py`.
 
To check that Django works, start the development server and open <http://127.0.0.1:8000>:
 
```bash
python manage.py runserver
```
 
## Configure the Database
 
New Django projects use SQLite, which is fine for development. For production, use PostgreSQL
or MariaDB: install the database server and its Python driver, then update `DATABASES` in
`settings.py`. See
[Get your database running](https://docs.djangoproject.com/en/stable/topics/install/#get-your-database-running)
and the [`DATABASES` reference](https://docs.djangoproject.com/en/stable/ref/settings/#databases).
 
## Install DDM
 
Install the DDM package. pip installs its
[dependencies](https://pypi.org/project/django-ddm/) automatically.
 
```bash
pip install django-ddm
```
 
Then update your project's `settings.py` and `urls.py` as described below.
 
### Update settings.py
 
**Installed apps.** Add DDM and its dependencies to `INSTALLED_APPS`:
 
```python
# settings.py
 
INSTALLED_APPS = [
    # ...
    'ddm',
    'ddm.auth',
    'ddm.logging',
    'ddm.questionnaire',
    'ddm.datadonation',
    'ddm.participation',
    'ddm.projects',
    'ddm.core',
    'django_ckeditor_5',
    'webpack_loader',
    'rest_framework',
    'rest_framework.authtoken',
]
```
 
!!! tip "App order matters if you customize templates"
 
    If you override DDM templates (see
    [Template Customization](configuration/customize_templates.md)), list the app that
    contains your overrides **before** `ddm.core`. Django's template loader searches
    `INSTALLED_APPS` in order and uses the first match.
 
**Static files and webpack-loader.** DDM's frontend ships as pre-built bundles that
`collectstatic` copies into `STATIC_ROOT`. If your settings don't define `STATIC_ROOT` yet, add
it:
 
```python
# settings.py
 
STATIC_ROOT = BASE_DIR / 'static'
```
 
Then add the webpack-loader configuration as-is:
 
```python
# settings.py
import os
 
WEBPACK_LOADER = {
    'DDM_UPLOADER': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/frontend/uploader/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm_core/frontend/uploader/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    },
    'DDM_QUESTIONNAIRE': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/frontend/questionnaire/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm_core/frontend/questionnaire/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    },
}
```
 
**Context processor.** Add the DDM context processor. It shows the installed DDM version below
the header of the researcher interface:
 
```python
# settings.py
 
TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                # ...
                'ddm.core.context_processors.add_ddm_version',
            ],
        },
    },
]
```

**Login redirects.** Set where users go after logging in and out. Without
`LOGIN_REDIRECT_URL`, Django sends users to `/accounts/profile/`, which doesn't exist:

```python
# settings.py

LOGIN_REDIRECT_URL = '/ddm/projects/'
LOGOUT_REDIRECT_URL = '/login/'
```

**CKEditor uploads.** Allow researchers to upload images in instructions and question texts,
and limit the file size:

```python
# settings.py

CKEDITOR_5_FILE_UPLOAD_PERMISSION = 'authenticated'
CKEDITOR_5_MAX_FILE_SIZE = 10  # In MB. The default, 0, means unlimited.
```

!!! danger "Allowing PDFs and videos"

    To also allow other file types, set `CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True` and list them
    in `CKEDITOR_5_UPLOAD_FILE_TYPES` (for example, `['jpeg', 'png', 'pdf', 'mp4']`). DDM then
    checks only the file extension, not the content, and any logged-in user can upload. Read
    [Security → CKEditor File Upload Security](security.md#ckeditor-file-upload-security)
    first.

For all CKEditor options, see the
[django-ckeditor-5 documentation](https://github.com/hvlads/django-ckeditor-5).

**Media files.** CKEditor stores uploaded files in Django's media storage. Set where to store
them and the URL to serve them from:

```python
# settings.py

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

**Time zone support.** DDM requires `USE_TZ = True`. New Django projects set this by default;
if you're adding DDM to an existing project, check it:
 
```python
# settings.py
 
USE_TZ = True
```
 
**DDM settings (optional).** Use `DDM_SETTINGS` to restrict who can create projects by email
pattern, or to adjust upload size and API rate limits:
 
```python
# settings.py
 
DDM_SETTINGS = {
    'EMAIL_PERMISSION_CHECK': r'.*(\.|@)somedomain\.com$',
}
```
 
For all DDM settings and their defaults, see [Settings Reference](settings_reference.md).
 
### Update urls.py
 
Add the DDM, login, logout, and CKEditor upload endpoints to your project's `urls.py`:
 
```python
# urls.py
from django.contrib.auth import views as auth_views
from django.urls import path, include
 
urlpatterns = [
    # ...
    path('ddm/', include('ddm.core.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='ddm_auth/login.html'), name='ddm_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='ddm_logout'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]
```
 
The `ddm_auth/login.html` template shows a password login form. To let researchers log in
through your institution instead, see [User Authentication](configuration/user_authentication.md).

To serve uploaded files during development, also add:

```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

!!! warning "Using DDM alongside Wagtail"
 
    If your site also runs [Wagtail](https://wagtail.org/) with internationalized URLs, set
    `prefix_default_language=False` in `i18n_patterns`. Otherwise, Wagtail's URL patterns can
    shadow DDM's:
 
    ```python
        # urls.py
        from django.conf.urls.i18n import i18n_patterns
        from django.urls import path, include
        from wagtail import urls as wagtail_urls
     
        urlpatterns += i18n_patterns(
            path('', include(wagtail_urls)),
            prefix_default_language=False,
        )
    ```
 
## Set Up the Database Tables
 
Create the database tables and a superuser account:
 
```bash
python manage.py migrate
python manage.py createsuperuser
```
 
## Test the Installation
 
Collect static files (required for the webpack-loader configuration) and start the server:
 
```bash
python manage.py collectstatic
python manage.py runserver
```
 
Then check both interfaces:
 
- <http://127.0.0.1:8000/admin>: Log in as the superuser and confirm that DDM appears in the
  Django admin site.
- <http://127.0.0.1:8000/ddm/projects>: Confirm that the project overview loads and that you
  can create a project.

## Prepare for Production
 
Before you expose your installation to the internet:
 
- **Harden Django.** New projects default to `DEBUG = True` and leave Django's other
  production settings (secure cookies, SSL redirect, HSTS) unset. Set `DEBUG = False` and run
  Django's deployment check:

```bash
    python manage.py check --deploy
```
 
    See the
    [Django deployment checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
    for what each check covers.
 
- **Serve static and media files.** With `DEBUG = False`, Django no longer serves static or
  uploaded files. Configure your web server (for example, Nginx) to serve `STATIC_ROOT` at
  `STATIC_URL` and `MEDIA_ROOT` at `MEDIA_URL`. See
  [Deploying static files](https://docs.djangoproject.com/en/stable/howto/static-files/deployment/).
- **Work through the DDM security checklist.** DDM uses `SECRET_KEY` to encrypt donated data,
  so losing or leaking it has consequences beyond a typical Django site. See the
  [Security checklist](security.md#checklist) before you generate and store it.
- **Throttle login attempts.** Django's login view has no brute-force protection. If you keep
  local password login (instead of only
  [OIDC login](configuration/user_authentication.md)), add throttling yourself, for example
  with [django-axes](https://github.com/jazzband/django-axes).

## Next Steps
 
- [Configuration](configuration/index.md): Set up institutional login, customize templates,
  and adjust the CKEditor toolbar.
- [Settings Reference](settings_reference.md): Look up all DDM settings, for example default
  header images for participation pages.
- [Security](security.md): Review security considerations for running DDM.
