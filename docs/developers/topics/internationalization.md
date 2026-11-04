# Internationalization

The researcher-facing Project Hub interface currently only supports English.

The participant-facing interface (briefing/donation/questionnaire/debriefing) currently supports
**English, German, Italian, and French**.

## Language Detection

The language in which the interface for participants is displayed is determined by the default
language of the participant's browser. If a language is not implemented for the participant
interface, it falls back to English.

## Adding Support for a New Language

Supporting a new language means adding translations in two separate places: the Django-rendered
parts of the participant flow, and the two Vue applications.

### Django Components

Only `ddm.participation` currently ships translations, at `ddm/participation/locale/`:

```text
ddm/participation/locale/
├── de/LC_MESSAGES/django.po
├── fr/LC_MESSAGES/django.po
└── it/LC_MESSAGES/django.po
```

(There is no `en/` directory — English is `LANGUAGE_CODE` in `test_project/settings.py`, so it's
the fallback/source language rather than a translated catalog.)

See the [Django i18n docs](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/) for
the full picture. To add or update a locale:

```console
cd ddm/participation
uv run --project ../.. django-admin makemessages -l de
```

`-l de` is the locale you want to create or update (`de`, `fr`, `it`, or a new one). This
creates/updates `ddm/participation/locale/<locale>/LC_MESSAGES/django.po` — add or edit
translations there. Then compile it to the `.mo` file gettext actually reads at runtime:

```console
uv run --project ../.. django-admin compilemessages
```

The other `ddm.*` sub-apps (`ddm.apis`, `ddm.auth`, `ddm.core`, `ddm.datadonation`, `ddm.logging`,
`ddm.projects`, `ddm.questionnaire`) each already wrap their `AppConfig.verbose_name` in
`gettext_lazy` (`_()`), but none of them ship a `locale/` directory yet — translating the
researcher-facing admin interface would mean adding one per app and marking up the rest of each
app's user-facing strings.

### Vue Components

Each Vue app manages its own translations with [vue-i18n](https://vue-i18n.intlify.dev/), as
plain JSON files under its own `src/locales/`:

```text
frontend/DDMUploader/src/locales/{en,de,fr,it}.json
frontend/DDMQuestionnaire/src/locales/{en,de,fr,it}.json
```

To add a new language, add the locale as a new top-level key to **both** apps' JSON files (the
Uploader and the Questionnaire are independent projects with independent translation files — see
[For Developers → Vue Integration](../index.md#vue-integration-frontend)) and fill in a
translation for every key already present for the other locales.

!!! warning "Don't edit the built copy"

    `ddm/core/static/ddm_core/frontend/uploader/locale/*.json` looks identical to
    `frontend/DDMUploader/src/locales/*.json`, but it's a **build artifact** — webpack copies it
    there from the source files whenever you run `npm run build` (see
    [Vue Integration](../index.md#vue-integration-frontend)). Edit the source files under
    `frontend/*/src/locales/`, never the copy under `ddm/core/static/`; your changes will be
    overwritten by the next build otherwise.

New translation keys only reach the served frontend after a rebuild (`npm run build`, or while
`npm run serve` is running during development).
