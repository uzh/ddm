# Documentation for Developers

This section of the documentation is targeted at people who contribute to the development of DDM or who want to
learn more about its development in general.

## Development Guidelines

### Local Project for Development and Testing

The repository includes a django test project that can be used for local development and testing.

#### Prerequisites

Development uses [uv](https://docs.astral.sh/uv/) to manage the Python interpreter, virtual
environment, and dependencies. Install it first — see the
[official installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
uv itself picks up the Python version from the repository's `.python-version` file (currently
`3.12`); it will download that interpreter automatically if you don't already have it.

#### Setup

##### Install required packages

Once you have cloned or forked the GitHub repository, run:

```
<...>/ddm> uv sync --group dev
```

This creates (or updates) a `.venv` in the repository root and installs the base runtime
dependencies plus the `dev` dependency group (test/lint tooling) as pinned in `uv.lock`. There's
no separate `python -m venv` step — `uv sync` manages the virtual environment for you. If you
also want to build the documentation locally, add the `docs` group: `uv sync --group dev --group docs`.

##### Install pre-commit hooks

```
<...>/ddm> uv run pre-commit install
<...>/ddm> uv run pre-commit install --hook-type pre-push   # enables pip-audit on push
```

##### Adjust Test Configuration

A basic standard configuration for the test project is specified in
`test_project/test_config.json`. Adjust the information in this file if you
want to use a custom setup, or use another database. By default, the test project
uses SQLite as a database backend.

If you do make changes to this file, please do NOT commit these changes to the
shared repository.

#### Commands

Prefix the regular django commands with `uv run` so they execute inside the project's managed
virtual environment:

##### Run Development Server

To start the development server use the following commands:

```
<...>/ddm> uv run python test_project/manage.py runserver
```

##### Create Database Migrations

To create new migrations based on the changes made to the models, run:

```
<...>/ddm> uv run python test_project/manage.py makemigrations
```

##### Apply migrations

To apply existing migrations to your local database, run: (If you are running a version of Python < 3.9, you might have to manually enable the JSON1 extension on SQLite for the migration to work properly. For an explanation on how to do this visit https://code.djangoproject.com/wiki/JSON1Extension.)

```
<...>/ddm> uv run python test_project/manage.py migrate
```

##### Run Unit Tests

To run unit tests, use:

```
<...>/ddm> uv run python test_project/manage.py test ddm
```

##### Lint and Format

Ruff and djLint are run automatically by pre-commit, but can also be run directly:

```
<...>/ddm> uv run ruff check .
<...>/ddm> uv run djlint .
```

##### Sass Compilation

To compile the scss file, sass is used. This is a separate, Node-based toolchain —
independent of the Python/uv setup above.

```
<...>/ddm/> npm install
<...>/ddm/> npm run sass:watch  # To run watcher during development
<...>/ddm/> npm run sass:build  # To build file for distribution
```

### Vue Integration (Frontend)

#### Development

First, install the appropriate node.js version according to the `.node-version` file. Then, install the
node dependencies:

```
(venv) <...>/ddm/frontend> npm install
```

To run the app in development mode, you will need to serve both Django’s dev server and the webpack development server:
From the frontend directory, run:

```
(venv) <...>/ddm/frontend> npm run serve
```

And, in a separate terminal in the Django root directory, run the Django development server:

```
(venv) <...>/ddm/test_project> python manage.py runserver
```

Open your locally hosted Django app in a browser (e.g. http://localhost:8000). Changes to the vue code will trigger an
automatic reload of the page in the browser.

#### Production Deployment

When it is time to deploy, or when you simply want to omit running the Vue dev server,
you can build the Vue project in production mode.
Cancel the `npm run serve` process if it is running and instead run `npm run build`.
The optimized bundles will be built in and placed into the Django static file location,
and webpack-stats.json will be updated to reflect this new configuration.
The vue builds should end up in the static folder of the django module (ddm/static).

#### Dependency updates

Dependencies of vue builds are regularly updated.

To update safely:

```
# Check for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix

# Check for outdated packages
npm outdated

# Update dependencies incrementally (minor updates to major updates)
npm install <packages>

# test updates
npm run lint
npm run test
npm run serve
npm run build
```

### CI/CD

This project uses _GitHub actions_ for automated testing and CI tasks.

#### GitHub Actions

All workflows install dependencies with `uv sync` from the committed `uv.lock`, so CI uses
exactly the same resolved dependency versions as local development.

A **push to develop** triggers build tests for the following configurations:

- Python: [3.12, 3.14]
- Database: [sqlite, mysql]

A **tag (vX.X.X) push to develop** triggers build tests (see above). If the tests are successful
develop is automatically merged into main.

!!! info

    Please make sure that pushed tags are in sync with the version in `pyproject.toml` (see
    [Release](#release) below).

    If the build-tests of a pushed tag fail, delete the tag (To delete a tag, first run `git tag -d tagname` then `git push --delete origin tagname`.) and push the fixed version again with the same tag until the tests run through.

A **push to main** triggers build tests and, if the tests are successful, builds and publishes
a new PyPI package using the version already set in `pyproject.toml` (see
[Release](#release) — there is no automatic version bump; the version must be set beforehand).
The tests have the same configurations as on develop.

A **pull request to main created by dependabot** will automatically update the
affected dependencies and merge into main.

#### Pipeline

A regular **push to develop** triggers the following pipeline:

1. Run tests on develop.
2. Create new documentation for GitHub pages.

A **tag ("vX.X.X") push to develop** triggers the following pipeline:

1. Run tests on develop.
2. Create new documentation for GitHub pages.
3. Merge develop into main.
4. Run tests on main.
5. Create PyPi package.

A **pull request to main created by dependabot** triggers the following pipeline:

1. Update dependencies.
2. Merge into main.
3. Run tests on main.
4. Create PyPi package.

#### Release

Releases are versioned statically in `pyproject.toml` — there is no tag-driven or
automatic version bumping. A new **release** is created manually:

1. Bump the version: `uv run uv version X.Y.Z` (or `uv version X.Y.Z` if `uv` is on your
   `PATH` directly). This updates the `version` field in `pyproject.toml`.
2. Commit the bump and, ideally, add a changelog entry.
3. Tag the commit `vX.Y.Z` and push the tag — this is what triggers the build/test/merge
   pipeline described above, and ultimately the PyPI publish.

Pre-releases follow the same flow with a [PEP 440](https://peps.python.org/pep-0440/)
pre-release version (e.g. `uv version 3.0.0b5`), tagged `preX.Y.Zb<n>`.

Publishing itself uses `uv build` + `uv publish` with
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — there is no
`PYPI_API_TOKEN` secret or `sed`-based version-stamping step involved anymore.

### Documentation

This documentation is written in Markdown and built with MkDocs + Material for MkDocs. See [Topics → Documentation](topics/documentation.md) for how to build it locally, how it is published, and how to regenerate the screenshots.
