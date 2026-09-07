# User Authentication

The Data Donation Module uses the default Django user management to authenticate users.

For production use in the context of an academic institution we recommend implementing
authentication through an academic authentication infrastructure with OpenID Connect (OIDC) - see below.
In the case of single user instances, i.e., if DDM is installed and
deployed to only support one specific project, this step is not necessary.

!!! note

    TODO: Explain creation of researcher profiles: 1. Login/Register through default authentication -> 2. Create a DDM research profile associated to authenticated account -> 3. redirect to ddm projects

For authentication to work properly make sure you do the following in your main site:

**Define a login and logout view in urls.py:**

```
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ...
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='ddm_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='ddm_logout'),
]
```

Either, you define your own template ('myapp/login.html'), or you can reuse or customize the default DDM login template
('ddm_auth/login.html' or 'ddm_auth/login_oidc.html' if you use OIDC authentication).

**Define Proper redirect paths in your settings.py:**

```
# Paths to redirect after login/logout
LOGIN_REDIRECT_URL = '/auth/researcher/'
LOGOUT_REDIRECT_URL = '/login/'
```

## Authentication With OpenID Connect (OIDC)

We recommend using the package [mozilla-django-oidc](https://github.com/mozilla/mozilla-django-oidc) for OIDC authentication.

### Setup


To enable OIDC authentication with `mozilla-django-oidc`, follow these steps (see also the
official `mozilla-django-oidc` documentation):

1. Set up a client with an OpenID provider.

2. Install `mozilla-django-oidc`: `pip install mozilla-django-oidc`

3. Adjust your `settings.py` — add `mozilla_django_oidc` to `INSTALLED_APPS` after
   `django.contrib.auth`:

    ```python
    INSTALLED_APPS = (
        # ...
        'django.contrib.auth',
        'mozilla_django_oidc',
        # ...
    )
    ```

4. Add the `mozilla_django_oidc` authentication backend:

    ```python
    AUTHENTICATION_BACKENDS = (
        'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
        # ...
    )
    ```

5. Add the following settings:

    ```python
    # API values retrieved from OIDC provider:
    OIDC_RP_CLIENT_ID = os.environ['OIDC_RP_CLIENT_ID']
    OIDC_RP_CLIENT_SECRET = os.environ['OIDC_RP_CLIENT_SECRET']

    # Look the following values up in your OIDC provider's documentation:
    OIDC_OP_AUTHORIZATION_ENDPOINT = '<URL of the OIDC OP authorization endpoint>'
    OIDC_OP_TOKEN_ENDPOINT = '<URL of the OIDC OP token endpoint>'
    OIDC_OP_USER_ENDPOINT = '<URL of the OIDC OP userinfo endpoint>'
    ```

6. Update `urls.py`:

    ```python
    urlpatterns = [
        # ...
        path('oidc/', include('mozilla_django_oidc.urls')),
        # ...
    ]
    ```

7. Enable token renewal by adding the following to your middlewares in `settings.py`:

    ```python
    MIDDLEWARE = [
        # middleware involving session and authentication must come first
        # ...
        'mozilla_django_oidc.middleware.SessionRefresh',
        # ...
    ]
    ```
