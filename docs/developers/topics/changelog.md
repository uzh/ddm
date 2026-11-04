# Changelog

`CHANGELOG.md` (repository root) follows these conventions, in place since February 2026
(entries from before that date may not match exactly).

## Headings

Each released version gets its own heading: `## X.Y.Z - YYYY-MM-DD`.

The topmost entry, for the version currently in development on `develop`, is the one exception:
it uses a single `#` instead of `##`, has no date, and its bullets carry no commit links yet
(e.g. the current `# 3.0.0` entry at the top of the file). Give it a proper `## X.Y.Z - YYYY-MM-DD`
heading and backfill the commit links only once that version is actually released.

## Sections

Use any of the following `###` sections that apply, in this order:

- `Fixed`
- `Added`
- `Changed`
- `Deprecated`
- `Removed`
- `Technical`
- `Security`
- `Documentation`
- `Update Guide` / `Migration Guide`

`Fixed`, `Added`, and `Changed` are written for a broad audience (researchers, administrators);
the rest are for a more technical audience and can assume developer knowledge.

Within `Changed` (and similarly for other sections, if a release touches many areas), bullets can
be grouped under a `#### *Area*` sub-heading, e.g. `#### *Uploader (data donation interface)*`,
`#### *Questionnaire*`, `#### *General*`.

`Update Guide` vs. `Migration Guide` — both describe what a site operator needs to do after
upgrading, but at different weights: use **`Update Guide`** for a short, one-off action (e.g. "run
`python manage.py collectstatic`"); use **`Migration Guide`** when a breaking change requires
step-by-step instructions, such as a settings key that changed shape. Don't use both for the
same release unless the release genuinely has both kinds of follow-up.

## Commit references

Every bullet should link back to the commit(s) it describes, as
`` [`shortsha`](https://github.com/uzh/ddm/commit/shortsha) ``, e.g.:

```markdown
- **File re-upload**: Clicking re-upload now opens file dialog directly (reduced from 2 clicks)
  ([`9ad0c39`](https://github.com/uzh/ddm/commit/9ad0c39)).
```

Multiple commits for one bullet are comma-separated, each with its own link.

## Worked example

```markdown
## 2.1.6 - 2025-11-19

### Fixed

- **Instruction deletion error**: Fixed crash when deleting instructions by removing reference
  to non-existent 'name' attribute ([`e12d104`](https://github.com/uzh/ddm/commit/e12d104)).
- **Upload failure modal**: Issue modal now displays correctly when all file uploads fail
  ([`d6577bd`](https://github.com/uzh/ddm/commit/d6577bd)).

### Changed

#### *General*

- **Translations**: Minor corrections to French and Italian translations
  ([`7ae9cb9`](https://github.com/uzh/ddm/commit/7ae9cb9)).

#### *Uploader (data donation interface)*

- **File re-upload**: Clicking re-upload now opens file dialog directly (reduced from 2 clicks)
  ([`9ad0c39`](https://github.com/uzh/ddm/commit/9ad0c39)).

### Update Guide

Run `python manage.py collectstatic` after upgrading to DDM v2.1.6 from the previous version.
```

See `CHANGELOG.md` itself for more real examples, including a `### Migration Guide` entry (the
`2.1.0` entry, for a `WEBPACK_LOADER` settings change).
