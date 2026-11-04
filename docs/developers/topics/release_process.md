# Release Process

This project is versioned with a single, static `version` field in `pyproject.toml` — there is
no automatic version bump anywhere. Which CI pipeline runs is decided purely by the **prefix of
the git tag you push**, independent of what the version string itself looks like. Keep that in
mind: a `v`-prefixed tag always merges `develop` into `main` and re-points the docs `latest`
alias, *even if* the version itself is a beta (e.g. `v3.0.0b5`) — only a `pre`-prefixed tag skips
that. Double-check the prefix before pushing.

## Regular release (`vX.Y.Z`)

Run these from a clean `develop` checkout, in order:

```console
uv version X.Y.Z
```

This writes `X.Y.Z` into `pyproject.toml`'s `version` field and re-locks `uv.lock`.

```console
git add pyproject.toml uv.lock
```

Also update `CHANGELOG.md`: promote the version's entry from the single-`#` placeholder used
during development to a proper `## X.Y.Z - YYYY-MM-DD` heading, and backfill its commit links
(see [Changelog Conventions](changelog.md)), then:

```console
git add CHANGELOG.md
git commit -m "chore: bump version to vX.Y.Z"
git push origin develop
```

Tag the commit you just pushed and push the tag — **the tag must start with `v`** and must
match the version you just set exactly:

```console
git tag vX.Y.Z
git push origin vX.Y.Z
```

Pushing that tag triggers `.github/workflows/merge-dev-to-main.yml`, which:

1. Runs the full test matrix (`test-ddm.yml`: Python 3.12 and 3.14, SQLite and MySQL).
2. If tests pass, publishes the docs under version `X.Y` (minor only, e.g. `3.0` from `v3.0.4`)
   via `publish-docs.yml`, and moves the `latest` alias to point at it.
3. Merges `develop` into `main` (`everlytic/branch-merge`, commit message
   `[Automated] Merged develop into target main`).

The push to `main` created by that merge then triggers `.github/workflows/publish-to-pypi.yml`,
which runs the tests again (MySQL only) and, if they pass, runs `uv build` followed by
`uv publish` — authenticated via PyPI Trusted Publishing (OIDC), no API token involved.

**If the tagged build fails:** delete the tag, fix the problem, and re-tag. Do **not** reuse a
tag name for different content once it's been pushed:

```console
git tag -d vX.Y.Z
git push origin --delete vX.Y.Z
# fix the problem, commit, push to develop again, then:
git tag vX.Y.Z
git push origin vX.Y.Z
```

## Pre-release (`preX.Y.Zb<n>`)

Use this for a beta/RC you want on PyPI and in the `dev` docs **without** touching `main` or the
`latest` docs alias.

```console
uv version X.Y.ZbN   # PEP 440 pre-release, e.g. 3.0.0b5
git add pyproject.toml uv.lock
git commit -m "chore: bump version to preX.Y.ZbN"
git push origin develop
```

Tag with a **`pre`-prefixed** tag (not `v`!) — the exact suffix only needs to start with `pre`,
but keep it matching the version for clarity:

```console
git tag preX.Y.ZbN
git push origin preX.Y.ZbN
```

Pushing a `pre*` tag triggers `.github/workflows/publish-prerelease-to-pypi.yml`, which:

1. Runs the test matrix against MySQL only.
2. Publishes the docs as the `dev` version (title "dev (develop)") — **not** `latest`.
3. Runs `uv build` + `uv publish`.

`develop` is never merged into `main` by this path.

## Other triggers

- **Plain push to `develop`** (no tag): runs the test matrix (`test-develop.yml`) and republishes
  the `dev` docs version — no PyPI publish.
- **Dependabot PR**: `dependabot-merge.yml` auto-approves and merges a dependency-bump PR that
  Dependabot itself already opened; it doesn't update any dependencies on its own, and merging it
  into `main` triggers `publish-to-pypi.yml` like any other push to `main`.
- **PR touching `docs/**`, `mkdocs.yml`, `pyproject.toml`, or `uv.lock`**: `docs-check.yml` runs
  `uv sync --group docs && uv run mkdocs build --strict` as a merge gate — it fails the PR if any
  internal link is broken or a page is missing from the nav. It does not deploy anything.

## Local setup for testing against MySQL

The CI matrix above includes MySQL; to reproduce that locally you need the `db-drivers` group,
which needs the MySQL client headers installed first (`mysqlclient` compiles against them):

```console
# macOS:
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="$(brew --prefix mysql-client)/lib/pkgconfig"

# Debian/Ubuntu:
sudo apt-get install default-libmysqlclient-dev pkg-config

uv sync --group dev --group db-drivers
```
