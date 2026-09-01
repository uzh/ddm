from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction

from ddm.core.utils.transfer.id_mapping import IdMap
from ddm.datadonation.transfer.services import build_blueprint, build_file_uploader
from ddm.projects.models import DonationProject
from ddm.projects.transfer.serialize import PROJECT_FIELDS
from ddm.questionnaire.transfer.services import build_questions

if TYPE_CHECKING:
    from ddm.projects.models import ResearchProfile


@transaction.atomic
def build_project(
    data: dict,
    *,
    owner: ResearchProfile,
    name: str,
    slug: str,
) -> tuple[DonationProject, list[str]]:
    """
    Create a new DonationProject (+ FileUploaders/DonationInstructions,
    DonationBlueprints and their nested config, and all questions) from a
    dict produced by `serialize_project()`.

    `owner`, `name`, `slug` are supplied by the caller (already reviewed/
    validated via the import or copy form) rather than read from `data` -
    a project's identity fields are never carried over as-is (see
    `ddm.projects.transfer.serialize.PROJECT_FIELDS`). `public_key` and
    `url_id` are left unset so `DonationProject.save()` generates fresh
    ones; the new project always starts with standard (non-"super secret")
    encryption, since the source's encryption password isn't retrievable.

    Returns (new_project, warnings) - warnings are the same non-fatal
    issues `build_questions()` can produce (e.g. an unresolved blueprint
    name reference), collected here for the caller to surface to the user.
    """
    id_map = IdMap()

    project_fields = {field: data["project"].get(field) for field in PROJECT_FIELDS}
    new_project = DonationProject(
        name=name,
        slug=slug,
        owner=owner,
        **project_fields,
    )
    # url_id and public_key are populated inside save() itself (see
    # DonationProject.save()), so they're still blank at this point and
    # must be excluded from validation here.
    new_project.full_clean(exclude=["url_id", "public_key"], validate_unique=False)
    new_project.save(force_insert=True)

    for fu_data in data.get("file_uploaders", []):
        build_file_uploader(fu_data, new_project, id_map=id_map, build_blueprints=False)

    for bp_data in data.get("blueprints", []):
        file_uploader = id_map.get(bp_data.get("file_uploader_local_id"))
        build_blueprint(
            bp_data, new_project, file_uploader=file_uploader, id_map=id_map
        )

    _, warnings = build_questions(
        data.get("questions", []), new_project, blueprint_id_map=id_map
    )

    return new_project, warnings
