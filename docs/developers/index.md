# Documentation for Developers

This section of the documentation is targeted at people who contribute to the development of DDM
or who want to learn more about its development in general.

## Repository Layout

`ddm` is a reusable Django app library, split into focused sub-apps under `ddm/`:

| Sub-app             | What it holds                                                                                                                                          |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ddm.projects`      | The `DonationProject` model and the researcher-facing Project Hub.                                                                                     |
| `ddm.datadonation`  | Upload blueprints and extraction/processing-rule configuration.                                                                                        |
| `ddm.questionnaire` | The built-in survey tool — questions, items, filters.                                                                                                  |
| `ddm.participation` | The participant-facing flow (briefing → donation → questionnaire → debriefing) and its views/models.                                                   |
| `ddm.auth`          | Researcher authentication and permissions (`ResearchProfile`, `ProjectAccessToken`).                                                                   |
| `ddm.apis`          | The REST API researchers can use to pull their project's data programmatically.                                                                        |
| `ddm.logging`       | Exception and event logging (`ExceptionLogEntry`, `EventLogEntry`).                                                                                    |
| `ddm.core`          | Shared utilities, templates, and static assets (CKEditor integration, HTML sanitization, color and template-rendering helpers) used by the apps above. |
| `ddm.encryption`    | Field-level encryption helpers — see [Topics → Encryption](topics/encryption.md).                                                                      |

`ddm.apis` and `ddm.encryption` define no models of their own, so unlike the others they aren't
listed in `INSTALLED_APPS`.

Two other top-level directories round out the repository:

- **`test_project/`** — the Django project that hosts `ddm` for local development and testing.
  It is a development harness, not a deployment reference; see
  [Administrators → Installation Guide](../administrators/installation.md) for how to actually
  configure a production Django project around `ddm`.
- **`frontend/`** — two independent Vue 3 + TypeScript applications, `DDMUploader` (the data
  donation/upload widget) and `DDMQuestionnaire` (the survey widget), each with its own
  `package.json`. Both are built with webpack and served into Django via
  [django-webpack-loader](https://github.com/django-webpack/django-webpack-loader). See
  [Vue Integration](#vue-integration-frontend) below.

## Development Guidelines

### Local Project for Development and Testing

The repository includes a Django test project that can be used for local development and testing.

#### Prerequisites

Development uses [uv](https://docs.astral.sh/uv/) to manage the Python interpreter, virtual
environment, and dependencies. Install it first — see the
[official installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
uv itself picks up the Python version from the repository's `.python-version` file (currently
`3.12`); it will download that interpreter automatically if you don't already have it.

#### Install required packages

Once you have cloned or forked the GitHub repository, run:

```console
uv sync --group dev
```

This creates (or updates) a `.venv` in the repository root and installs the base runtime
dependencies plus the `dev` dependency group (test/lint tooling) as pinned in `uv.lock`. There's
no separate `python -m venv` step — `uv sync` manages the virtual environment for you. If you
also want to build the documentation locally, add the `docs` group:
`uv sync --group dev --group docs`. If you need to test against MySQL (not just the SQLite
default), see [Release Process → Local setup for testing against MySQL](topics/release_process.md#local-setup-for-testing-against-mysql).

#### Install pre-commit hooks

```console
uv run pre-commit install
uv run pre-commit install --hook-type pre-push   # enables pip-audit on push
```

The second command matters: the `pip-audit` hook in `.pre-commit-config.yaml` is pinned to the
`pre-push` stage, so it won't run at all unless you also install hooks for that stage
specifically.

#### Configure local settings

`test_project/settings.py` loads a `.env` file (via `python-dotenv`) if one exists at the
repository root. By default (no `.env`), the test project uses SQLite at `ddmtestdb`, an empty
`SECRET_KEY`, and `DDM_STRICT_CSP` off. Create a `.env` at the repository root to override any of:

```text
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=ddmtestdb
DB_USER=ddmtestuser
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=
SECRET_KEY=
DDM_STRICT_CSP=
```

`.env` is git-ignored — never commit it; it's meant for your own local overrides (e.g. pointing
at a local MySQL instance, or setting a real `SECRET_KEY` to test encryption behavior that
depends on it).

Prefix the regular Django commands below with `uv run` so they execute inside the project's
managed virtual environment.

#### Run Development Server

```console
uv run python test_project/manage.py runserver
```

#### Create Database Migrations

To create new migrations based on the changes made to the models, run:

```console
uv run python test_project/manage.py makemigrations
```

#### Apply migrations

```console
uv run python test_project/manage.py migrate
```

#### Run Unit Tests

```console
uv run python test_project/manage.py test ddm
```

Run a single app's tests (faster while iterating) by narrowing the target, e.g.
`uv run python test_project/manage.py test ddm.core`.

#### Code style & checks

Ruff (lint + format) and djLint (Django template lint) run automatically via pre-commit. Ruff is
a `dev` dependency, so it can also be run directly:

```console
uv run ruff check .          # lint
uv run ruff format .         # format
```

djLint is **not** a project dependency — pre-commit runs it in its own isolated environment, so
`uv run djlint` won't work. Run it standalone with `uvx`, pinned to the same version pre-commit
uses (`v1.36.4` in `.pre-commit-config.yaml` at the time of writing):

```console
uvx djlint==1.36.4 ddm --check
```

To run the same dependency-vulnerability scan the `pip-audit` pre-push hook runs, without
pushing:

```console
uv export --no-hashes --no-emit-project --group dev -o /tmp/ddm-deps.txt
uv run pip-audit -r /tmp/ddm-deps.txt
```

A `[tool.coverage]` configuration (80% minimum, `ddm/**` only) is set up in `pyproject.toml` for
local use with `coverage run`/`coverage report`, but it isn't currently wired into CI, and
running it as configured requires the `django_coverage_plugin` package, which isn't in the `dev`
dependency group yet — add it yourself (`uv add --group dev django_coverage_plugin`) if you want
to use it locally.

#### Sass Compilation

To compile the scss file, sass is used. This is a separate, Node-based toolchain —
independent of the Python/uv setup above.

```console
npm install
npm run sass:watch  # run the watcher during development
npm run sass:build  # build the compressed file for distribution
```

### Vue Integration (Frontend)

`frontend/DDMUploader` and `frontend/DDMQuestionnaire` are two separate Vue 3 + TypeScript
projects — each has its own `package.json`, its own `.node-version` (currently `v20.18.0` for
both), and must be installed/run independently. Everything below applies to each one; just `cd`
into the one you're working on.

#### Development

First, install the Node.js version pinned in that project's `.node-version` (e.g. with
[nvm](https://github.com/nvm-sh/nvm): `nvm install` from inside the project directory). Then
install dependencies:

```console
npm install
```

To run the app in development mode, serve both the webpack dev server and Django's dev server at
the same time. From the project directory:

```console
npm run serve
```

And, in a separate terminal from the repository root, the Django dev server:

```console
uv run python test_project/manage.py runserver
```

Open your locally hosted Django app in a browser (e.g. <http://localhost:8000>). Changes to the
Vue code trigger an automatic reload in the browser.

#### Lint and test

```console
npm run lint   # eslint --ext .ts,.vue src
npm run test   # vitest
```

#### Production build

When it's time to deploy, or to stop running the dev server, cancel `npm run serve` and build the
production bundle instead:

```console
npm run build
```

The optimized bundles are written into the Django static file locations under `ddm/core/static/`,
and the corresponding `webpack-stats.json` is updated so `django-webpack-loader` picks up the new
build.

#### Dependency updates

```console
npm audit            # check for vulnerabilities
npm audit fix         # fix what can be fixed automatically
npm outdated          # check for outdated packages
npm install <package> # update one package deliberately
npm run lint && npm run test && npm run build  # verify nothing broke
```

Repeat for the other frontend project — updates are independent per project.

### Contributing

- **Branches**: `develop` is the integration branch; day-to-day work and PRs target it. `main`
  only ever receives merges from `develop` via the release pipeline (see
  [Release Process](topics/release_process.md)) — don't push or PR directly to `main`.
- **Before opening a PR**: make sure `uv run pre-commit run --all-files` is clean, the test suite
  passes (`uv run python test_project/manage.py test ddm`), and — if your change touches
  user-facing behavior — `CHANGELOG.md`'s current unreleased entry has a bullet describing it
  (see [Changelog Conventions](topics/changelog.md)).
- **Docs**: if you change anything under `docs/`, `mkdocs.yml`, `pyproject.toml`, or `uv.lock`,
  `docs-check.yml` will build the site with `mkdocs build --strict` on your PR — fix any broken
  link or nav entry it reports before merging.

### CI/CD and Releases

This project uses GitHub Actions for testing and release automation; every workflow installs
dependencies with `uv sync` from the committed `uv.lock`, so CI uses exactly the same resolved
dependency versions as local development. For the full release procedure — regular releases,
pre-releases, and what triggers what — see **[Topics → Release Process](topics/release_process.md)**.

### Documentation

This documentation is written in Markdown and built with MkDocs + Material for MkDocs. See
[Topics → Documentation](topics/documentation.md) for how to build it locally, how it is
published, and how to regenerate the screenshots.
