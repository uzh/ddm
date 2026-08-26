from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 1
SUPPORTED_SCHEMA_VERSIONS = {1}

EXPORT_KIND_PROJECT = "project"
EXPORT_KIND_BLUEPRINT = "blueprint"
EXPORT_KIND_QUESTIONNAIRE = "questionnaire"
VALID_EXPORT_KINDS = {
    EXPORT_KIND_PROJECT,
    EXPORT_KIND_BLUEPRINT,
    EXPORT_KIND_QUESTIONNAIRE,
}


class TransferValidationError(Exception):
    """
    Raised when an export/import payload fails structural validation.

    Carries the full list of problems found (rather than failing on the
    first one) so the importing user can fix a malformed/incompatible file
    in one pass instead of one error at a time.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def _validate_schema_version_and_kind(
    data: dict, *, expected_kind: str, errors: list[str]
) -> None:
    schema_version = data.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(
            f'Unsupported file version "{schema_version}". This DDM '
            f"instance supports schema version(s): "
            f"{sorted(SUPPORTED_SCHEMA_VERSIONS)}."
        )

    export_kind = data.get("export_kind")
    if export_kind != expected_kind:
        errors.append(
            f'This import expects a "{expected_kind}" export file, but the '
            f'uploaded file is a "{export_kind}" export.'
        )


def _validate_sections_for_kind(
    data: dict, *, expected_kind: str, errors: list[str]
) -> None:
    if expected_kind == EXPORT_KIND_PROJECT:
        for key in ("project", "file_uploaders", "blueprints", "questions"):
            expected_type = dict if key == "project" else list
            if not isinstance(data.get(key), expected_type):
                errors.append(f'Missing or invalid "{key}" section.')

    if expected_kind == EXPORT_KIND_BLUEPRINT:
        blueprints = data.get("blueprints")
        if not isinstance(blueprints, list) or len(blueprints) != 1:
            errors.append('Expected exactly one entry in the "blueprints" section.')

    if expected_kind == EXPORT_KIND_QUESTIONNAIRE and not isinstance(
        data.get("questions"), list
    ):
        errors.append('Missing or invalid "questions" section.')


def validate_envelope(data: Any, *, expected_kind: str) -> None:  # noqa: ANN401
    """
    Validate the top-level shape of an export payload before any DB access.

    Only checks structure (schema_version, export_kind, presence of the
    top-level sections relevant to `expected_kind`, and filter condition
    references) - per-field validity is left to the model layer's own
    `clean()`/`full_clean()` during build, so validation rules aren't
    duplicated in two places.
    """
    if not isinstance(data, dict):
        raise TransferValidationError(["File does not contain a valid export object."])

    errors: list[str] = []
    _validate_schema_version_and_kind(data, expected_kind=expected_kind, errors=errors)
    _validate_sections_for_kind(data, expected_kind=expected_kind, errors=errors)

    if errors:
        raise TransferValidationError(errors)

    questions = data.get("questions")
    if isinstance(questions, list):
        _validate_filter_condition_refs(questions, errors)

    if errors:
        raise TransferValidationError(errors)


def _collect_known_local_ids(questions: list, errors: list[str]) -> set[str]:
    known_ids: set[str] = set()
    for q in questions:
        if not isinstance(q, dict):
            errors.append('Malformed entry in "questions" section.')
            continue
        if q.get("local_id"):
            known_ids.add(q["local_id"])
        for item in q.get("items") or []:
            if isinstance(item, dict) and item.get("local_id"):
                known_ids.add(item["local_id"])
    return known_ids


def _validate_filter_conditions_for_question(
    q: dict, known_ids: set[str], errors: list[str]
) -> None:
    label = q.get("name") or q.get("variable_name") or q.get("local_id") or "?"
    for fc in q.get("filter_conditions") or []:
        if not isinstance(fc, dict):
            errors.append(f'Malformed filter condition on question "{label}".')
            continue

        target_local_id = fc.get("target_local_id")
        if target_local_id not in known_ids:
            errors.append(
                f'Filter condition on question "{label}" references an '
                f"unknown target ({target_local_id!r})."
            )

        if fc.get("source_type") in ("question", "item"):
            source_local_id = fc.get("source_local_id")
            if source_local_id not in known_ids:
                errors.append(
                    f'Filter condition on question "{label}" references '
                    f"an unknown source ({source_local_id!r})."
                )


def _validate_filter_condition_refs(questions: list, errors: list[str]) -> None:
    """
    Filter condition target/FK-source references have no defined "drop it"
    fallback (unlike e.g. backup_for or a blueprint link) - a dangling one
    means the file is malformed, so it's rejected here rather than risking
    an inconsistent object being built.
    """
    known_ids = _collect_known_local_ids(questions, errors)
    for q in questions:
        if isinstance(q, dict):
            _validate_filter_conditions_for_question(q, known_ids, errors)
