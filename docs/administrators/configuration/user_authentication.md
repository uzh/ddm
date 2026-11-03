# User Authentication
 
DDM uses Django's built-in user management. Researchers log in with a Django user account,
either with a local password or through your institution's login. The
[Installation Guide](../installation.md) sets up local password login; this page explains who
gets researcher access and how to add institutional login.
 
For institutional deployments, we recommend login through OpenID Connect (OIDC); see
[Set Up OIDC Login](#set-up-oidc-login). If you run DDM only for yourself or a few trusted
users, local password login is enough.
 
## Access Control
 
There's no separate registration for DDM. When a logged-in user opens a researcher page for
the first time, DDM creates a research profile for them automatically. DDM then grants access
if one of the following is true:
 
- The user is a superuser.
- The user's email address matches `DDM_SETTINGS['EMAIL_PERMISSION_CHECK']`.
- The user's research profile has **Ignore email restriction** enabled.
- `EMAIL_PERMISSION_CHECK` isn't set.

Users without access see a "no permission" page instead of the project list.
 
!!! warning "Set an email restriction"
 
    If you don't set `EMAIL_PERMISSION_CHECK`, every user who can log in gets researcher
    access. With OIDC, that includes everyone your provider authenticates, because
    `mozilla-django-oidc` creates accounts automatically on first login. See
    [Settings Reference](../settings_reference.md).
 
### Grant Access to an Individual User
 
To give access to someone whose email doesn't match the restriction (for example, an external
collaborator):
 
1. Open the Django admin site (`/admin/`) and log in as a superuser.
2. Open the user's research profile.
3. Enable **Ignore email restriction** and save.

## Set Up OIDC Login
 
We recommend [mozilla-django-oidc](https://github.com/mozilla/mozilla-django-oidc) for OIDC
login. The steps below cover the basic setup; for all options, see the
[mozilla-django-oidc documentation](https://mozilla-django-oidc.readthedocs.io/).
 
1. **Register a client with your OIDC provider.** Use
   `https://<your-domain>/oidc/callback/` as the redirect URI. Note the client ID and client
   secret that the provider gives you.

2. **Install the package:**

```bash
    pip install mozilla-django-oidc
```
 
3. **Add the app** to `INSTALLED_APPS`, after `django.contrib.auth`:

```python
    # settings.py
 
    INSTALLED_APPS = [
        # ...
        'django.contrib.auth',
        'mozilla_django_oidc',
        # ...
    ]
```
 
4. **Add the authentication backend.** Keep Django's `ModelBackend` if you still want local
   password login, for example for the superuser:

```python
    # settings.py
 
    AUTHENTICATION_BACKENDS = [
        'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
        'django.contrib.auth.backends.ModelBackend',  # Optional: keeps local password login.
    ]
```
 
5. **Add the provider settings.** Read the client ID and secret from the environment or a
   secrets manager; don't hardcode them. Look up the endpoint URLs in your provider's
   documentation.

```python
    # settings.py
    import os
 
    OIDC_RP_CLIENT_ID = os.environ['OIDC_RP_CLIENT_ID']
    OIDC_RP_CLIENT_SECRET = os.environ['OIDC_RP_CLIENT_SECRET']
 
    OIDC_OP_AUTHORIZATION_ENDPOINT = '<authorization endpoint URL>'
    OIDC_OP_TOKEN_ENDPOINT = '<token endpoint URL>'
    OIDC_OP_USER_ENDPOINT = '<userinfo endpoint URL>'
```
 
Most providers sign tokens with RS256. If yours does, also set:
 
```python
    OIDC_RP_SIGN_ALGO = 'RS256'
    OIDC_OP_JWKS_ENDPOINT = '<JWKS endpoint URL>'
```
 
6. **Add the OIDC URLs** to `urls.py`, and switch the login view to DDM's OIDC login template,
   which shows a login button instead of a password form:

```python
    # urls.py
 
    urlpatterns = [
        # ...
        path('oidc/', include('mozilla_django_oidc.urls')),
        path('login/', auth_views.LoginView.as_view(template_name='ddm_auth/login_oidc.html'), name='ddm_login'),
        # ...
    ]
```
 
7. **Optional: Enable session refresh.** To re-check users with the provider when their token
   expires, add the middleware after Django's session and authentication middleware:

```python
    # settings.py
 
    MIDDLEWARE = [
        # ...
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'mozilla_django_oidc.middleware.SessionRefresh',
        # ...
    ]
```
 
## Notes
 
!!! info "No built-in multi-factor authentication"
 
    DDM doesn't provide multi-factor authentication (MFA) for local password login. To require
    MFA, enforce it at your OIDC provider (recommended) or add a third-party Django MFA
    package.
 
!!! note "API access uses project tokens, not logins"
 
    The settings on this page control access to the researcher interface. The researcher API
    uses separate per-project access tokens that researchers create within their project. See
    [Researchers → APIs](../../researchers/topics/apis.md).
