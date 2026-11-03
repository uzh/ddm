# System Administrators

Use this section to set up and maintain a server that hosts DDM data donation
projects, either for yourself or for your institution.

## Requirements

DDM is a Django app, not a standalone server: it runs inside a Django project
that you host. You need:

- A server that can run a Python/Django application.
- A database. SQLite works for testing; use PostgreSQL or MariaDB in production.
- Optional: Access to an OpenID Connect (OIDC) provider, if researchers should
  log in with their institutional account. See
  [User Authentication](configuration/user_authentication.md).

## In this section

- [Installation Guide](installation.md): Install DDM and get it running.
- [Configuration](configuration/index.md): Set up user authentication and
  customize admin templates and the CKEditor text editor.
- [Settings Reference](settings_reference.md): Look up all available DDM settings.
- [Security](security.md): Secure your DDM installation.
