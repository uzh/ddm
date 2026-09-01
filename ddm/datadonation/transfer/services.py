from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from ddm import VERSION as DDM_VERSION
from ddm.core.utils.transfer.id_mapping import AllocationIDs, IdMap, LocalIdAllocator
from ddm.core.utils.transfer.schema import (
    EXPORT_KIND_BLUEPRINT,
    EXPORT_KIND_FILE_UPLOADER,
    SCHEMA_VERSION,
)
from ddm.datadonation.models import (
    BlueprintFilePath,
    DonationBlueprint,
    DonationInstruction,
    ExtractionField,
    FileUploader,
    ProcessingRule,
)

if TYPE_CHECKING:
    from ddm.projects.models import DonationProject


def _blueprint_name_available_in_project(name: str, project: DonationProject) -> bool:
    # Scoped to the target project
    return not DonationBlueprint.objects.filter(project=project, name=name).exists()


@transaction.atomic
def copy_blueprint(blueprint: DonationBlueprint) -> DonationBlueprint:
    new_bp = copy.deepcopy(blueprint)
    new_bp.pk = None

    base_name = f"{blueprint.name}_copy"
    new_name = base_name
    i = 0
    while not _blueprint_name_available_in_project(new_name, new_bp.project):
        i += 1
        new_name = f"{base_name}_{i}"
    new_bp.name = new_name
    new_bp.save(force_insert=True)

    # copy file paths
    for fp in blueprint.blueprintfilepath_set.all():
        fp_new = copy.copy(fp)
        fp_new.pk = None
        fp_new.blueprint = new_bp
        fp_new.save(force_insert=True)

    # copy extraction field & extraction rules
    for field in blueprint.extractionfield_set.all():
        field_new = copy.copy(field)
        field_new.pk = None
        field_new.blueprint = new_bp
        field_new.save(force_insert=True)

        for rule in field.processingrule_set.all():
            rule_new = copy.copy(rule)
            rule_new.pk = None
            rule_new.field = field_new
            rule_new.blueprint = new_bp
            rule_new.save(force_insert=True)

    return new_bp


def serialize_blueprint(
    blueprint: DonationBlueprint,
    allocator: LocalIdAllocator,
    *,
    include_file_uploader_ref: bool = False,
) -> dict:
    """
    Serialize a DonationBlueprint (+ nested BlueprintFilePath,
    ExtractionField, ProcessingRule) into a JSON-safe dict for export.

    Cross-references (backup_for, file_uploader, extraction fields) are
    represented as namespaced local ids assigned via `allocator`, never as
    real primary keys. `include_file_uploader_ref` is only set when this
    blueprint is exported as part of a whole-project export - a standalone
    blueprint export never references a file uploader, since attaching to
    one is a target-project decision made at import time.
    """
    local_id = allocator.get_or_create(AllocationIDs.BLUEPRINT, blueprint.pk)

    file_uploader_local_id = None
    if include_file_uploader_ref and blueprint.file_uploader_id:
        file_uploader_local_id = allocator.get_or_create(
            AllocationIDs.FILE_UPLOADER, blueprint.file_uploader_id
        )

    backup_for_local_id = None
    if blueprint.backup_for_id:
        backup_for_local_id = allocator.get_or_create(
            AllocationIDs.BLUEPRINT, blueprint.backup_for_id
        )

    file_paths = [
        {"path": fp.path, "is_regex": fp.is_regex, "priority": fp.priority}
        for fp in blueprint.blueprintfilepath_set.all()
    ]

    extraction_fields = []
    field_local_ids: dict[int, str] = {}
    for field in blueprint.extractionfield_set.all():
        field_local_id = allocator.get_or_create(
            AllocationIDs.EXTRACTION_FIELD, field.pk
        )
        field_local_ids[field.pk] = field_local_id
        extraction_fields.append(
            {
                "local_id": field_local_id,
                "scope": field.scope,
                "expected_name": field.expected_name,
                "match_regex": field.match_regex,
                "keep_in_donation": field.keep_in_donation,
                "alias": field.alias,
            }
        )

    # Iterate rules directly off the blueprint (not via field.processingrule_set)
    # so rules with no associated field (field=SET_NULL) are captured too.
    processing_rules = [
        {
            "name": rule.name,
            "field_local_id": field_local_ids.get(rule.field_id),
            "execution_order": rule.execution_order,
            "comparison_operator": rule.comparison_operator,
            "comparison_value": rule.comparison_value,
            "replacement_value": rule.replacement_value,
        }
        for rule in blueprint.processingrule_set.all().order_by("execution_order")
    ]

    return {
        "local_id": local_id,
        "file_uploader_local_id": file_uploader_local_id,
        "name": blueprint.name,
        "description": blueprint.description,
        "display_name": blueprint.display_name,
        "display_position": blueprint.display_position,
        "exp_file_format": blueprint.exp_file_format,
        "parser_config": blueprint.parser_config,
        "expected_fields": blueprint.expected_fields,
        "expected_fields_regex_matching": blueprint.expected_fields_regex_matching,
        "nested_expected_fields": blueprint.nested_expected_fields,
        "nested_expected_fields_regex_matching": (
            blueprint.nested_expected_fields_regex_matching
        ),
        "nested_display_by_root_item": blueprint.nested_display_by_root_item,
        "nested_entry_exclusion_allowed": blueprint.nested_entry_exclusion_allowed,
        "backup_for_local_id": backup_for_local_id,
        "backup_priority": blueprint.backup_priority,
        "regex_path": blueprint.regex_path,
        "file_paths": file_paths,
        "extraction_fields": extraction_fields,
        "processing_rules": processing_rules,
    }


@transaction.atomic
def build_blueprint(
    data: dict,
    project: DonationProject,
    *,
    file_uploader: FileUploader | None = None,
    id_map: IdMap | None = None,
) -> DonationBlueprint:
    """
    Create a new DonationBlueprint (+ nested BlueprintFilePath,
    ExtractionField, ProcessingRule) in `project`, from a dict produced by
    `serialize_blueprint()`.

    `id_map` is shared across a whole-project build so `backup_for` can
    resolve to a sibling blueprint created earlier in the same import; for
    a standalone blueprint import a fresh IdMap is created, so backup_for
    always resolves to None (no sibling blueprint is part of the import).
    `file_uploader` must already be resolved by the caller - the blueprint
    build itself doesn't interpret `file_uploader_local_id`.
    """
    if id_map is None:
        id_map = IdMap()

    base_name = data["name"]
    new_name = base_name
    suffix = 0
    while not _blueprint_name_available_in_project(new_name, project):
        suffix += 1
        new_name = f"{base_name}_{suffix}"

    new_bp = DonationBlueprint(
        project=project,
        file_uploader=file_uploader,
        name=new_name,
        description=data.get("description", ""),
        display_name=data.get("display_name", ""),
        display_position=data.get("display_position", 1),
        exp_file_format=data.get(
            "exp_file_format", DonationBlueprint.FileFormats.JSON_FORMAT
        ),
        parser_config=data.get("parser_config"),
        expected_fields=data.get("expected_fields", ""),
        expected_fields_regex_matching=data.get(
            "expected_fields_regex_matching", False
        ),
        nested_expected_fields=data.get("nested_expected_fields", ""),
        nested_expected_fields_regex_matching=data.get(
            "nested_expected_fields_regex_matching", False
        ),
        nested_display_by_root_item=data.get("nested_display_by_root_item", False),
        nested_entry_exclusion_allowed=data.get(
            "nested_entry_exclusion_allowed", False
        ),
        backup_for=id_map.get(data.get("backup_for_local_id")),
        backup_priority=data.get("backup_priority", 0),
        regex_path=data.get("regex_path", ""),
    )
    new_bp.full_clean(validate_unique=False)
    new_bp.save(force_insert=True)
    id_map.register(data.get("local_id"), new_bp)

    for fp in data.get("file_paths", []):
        BlueprintFilePath.objects.create(
            blueprint=new_bp,
            path=fp.get("path", ""),
            is_regex=fp.get("is_regex", False),
            priority=fp.get("priority", 1),
        )

    for field_data in data.get("extraction_fields", []):
        field = ExtractionField.objects.create(
            blueprint=new_bp,
            scope=field_data.get("scope", ExtractionField.Scope.ROOT),
            expected_name=field_data.get("expected_name", ""),
            match_regex=field_data.get("match_regex", False),
            keep_in_donation=field_data.get("keep_in_donation", False),
            alias=field_data.get("alias", ""),
        )
        id_map.register(field_data.get("local_id"), field)

    for rule_data in data.get("processing_rules", []):
        ProcessingRule.objects.create(
            blueprint=new_bp,
            name=rule_data.get("name", ""),
            field=id_map.get(rule_data.get("field_local_id")),
            execution_order=rule_data.get("execution_order", 1),
            comparison_operator=rule_data.get("comparison_operator"),
            comparison_value=rule_data.get("comparison_value", ""),
            replacement_value=rule_data.get("replacement_value", ""),
        )

    return new_bp


def export_blueprint(blueprint: DonationBlueprint) -> dict:
    """Wraps `serialize_blueprint()` in a standalone export envelope."""
    return {
        "schema_version": SCHEMA_VERSION,
        "export_kind": EXPORT_KIND_BLUEPRINT,
        "exported_at": timezone.now().isoformat(),
        "ddm_version": DDM_VERSION,
        "blueprints": [serialize_blueprint(blueprint, LocalIdAllocator())],
    }


def _file_uploader_name_available_in_project(
    name: str, project: DonationProject
) -> bool:
    # Scoped to the target project
    return not FileUploader.objects.filter(project=project, name=name).exists()


def serialize_file_uploader(
    uploader: FileUploader,
    allocator: LocalIdAllocator,
    *,
    include_blueprints: bool = True,
) -> dict:
    """
    Serialize a FileUploader (+ nested DonationInstruction) into a JSON-safe
    dict for export.

    `include_blueprints=True` (the default) bundles
    every blueprint currently attached to this uploader, each serialized
    via `serialize_blueprint(..., include_file_uploader_ref=True)` so it
    carries a `file_uploader_local_id` pointing back at this same uploader.
    A whole-project export passes `include_blueprints=False`, since
    blueprints are already enumerated once at the project's top level.
    """
    local_id = allocator.get_or_create(AllocationIDs.FILE_UPLOADER, uploader.pk)

    instructions = [
        {"index": instr.index, "text": instr.text}
        for instr in uploader.donationinstruction_set.all()
    ]

    data = {
        "local_id": local_id,
        "name": uploader.name,
        "display_name": uploader.display_name,
        "upload_type": uploader.upload_type,
        "extract_nested_zips": uploader.extract_nested_zips,
        "extraction_depth": uploader.extraction_depth,
        "combined_consent": uploader.combined_consent,
        "instructions": instructions,
    }

    if include_blueprints:
        data["blueprints"] = [
            serialize_blueprint(bp, allocator, include_file_uploader_ref=True)
            for bp in uploader.donationblueprint_set.all()
        ]

    return data


@transaction.atomic
def build_file_uploader(
    data: dict,
    project: DonationProject,
    *,
    id_map: IdMap | None = None,
    build_blueprints: bool = True,
) -> FileUploader:
    """
    Create a new FileUploader (+ nested DonationInstruction) in `project`,
    from a dict produced by `serialize_file_uploader()`.

    `index` is always left unset so `FileUploader.save()` appends it after
    the target project's existing uploaders, rather than carrying over the
    source's index value - the source's exact position isn't meaningful in
    a different (possibly non-empty) target project.

    When `build_blueprints` (the default), also builds every bundled
    blueprint, attached directly to the newly created uploader - no
    `file_uploader_local_id` lookup needed, since every bundled blueprint
    belongs to this one uploader by construction. Called with
    `build_blueprints=False` from the whole-project path, where blueprints
    are built separately afterward.
    """
    if id_map is None:
        id_map = IdMap()

    base_name = data["name"]
    new_name = base_name
    suffix = 0
    while not _file_uploader_name_available_in_project(new_name, project):
        suffix += 1
        new_name = f"{base_name}_{suffix}"

    new_uploader = FileUploader.objects.create(
        project=project,
        name=new_name,
        display_name=data.get("display_name", ""),
        upload_type=data.get("upload_type", FileUploader.UploadTypes.SINGLE_FILE),
        extract_nested_zips=data.get("extract_nested_zips", False),
        extraction_depth=data.get("extraction_depth", 0),
        combined_consent=data.get("combined_consent", False),
    )
    id_map.register(data.get("local_id"), new_uploader)

    for instr_data in data.get("instructions", []):
        DonationInstruction.objects.create(
            file_uploader=new_uploader,
            index=instr_data.get("index", 1),
            text=instr_data.get("text", ""),
        )

    if build_blueprints:
        for bp_data in data.get("blueprints", []):
            build_blueprint(bp_data, project, file_uploader=new_uploader, id_map=id_map)

    return new_uploader


def export_file_uploader(uploader: FileUploader) -> dict:
    """Wraps `serialize_file_uploader()` in a standalone export envelope."""
    return {
        "schema_version": SCHEMA_VERSION,
        "export_kind": EXPORT_KIND_FILE_UPLOADER,
        "exported_at": timezone.now().isoformat(),
        "ddm_version": DDM_VERSION,
        "file_uploader": serialize_file_uploader(
            uploader, LocalIdAllocator(), include_blueprints=True
        ),
    }
