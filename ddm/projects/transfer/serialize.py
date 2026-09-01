from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils import timezone

from ddm import VERSION as DDM_VERSION
from ddm.core.utils.transfer.id_mapping import LocalIdAllocator
from ddm.core.utils.transfer.schema import EXPORT_KIND_PROJECT, SCHEMA_VERSION
from ddm.datadonation.transfer.services import (
    serialize_blueprint,
    serialize_file_uploader,
)
from ddm.questionnaire.transfer.services import serialize_questions

if TYPE_CHECKING:
    from ddm.projects.models import DonationProject

# DonationProject fields carried over on export/copy. Deliberately excludes:
# - id, url_id, slug, date_created, owner, public_key: identity/access
#   fields, resolved fresh at import/copy time (see build_project()).
# - img_header_left, img_header_right: skipped in v1.
# - super_secret: can never be carried over - the source's encryption
#   password isn't retrievable (see build_project()), so a new project
#   always starts with standard encryption regardless of the source.
# - active: administrative lifecycle flag, not "content" config; a new
#   project always starts active, matching regular project creation.
PROJECT_FIELDS = [
    "contact_information",
    "data_protection_statement",
    "briefing_text",
    "briefing_consent_enabled",
    "briefing_consent_label_yes",
    "briefing_consent_label_no",
    "debriefing_text",
    "show_project_title",
    "primary_color",
    "background_color",
    "redirect_enabled",
    "redirect_target",
    "url_parameter_enabled",
    "expected_url_parameters",
    "custom_uploader_translations",
]


def export_project(project: DonationProject) -> dict:
    """
    Serialize a DonationProject (+ FileUploaders/DonationInstructions,
    DonationBlueprints and their nested config, and all questions) into a
    JSON-safe envelope for export or in-app copy.

    Collected/participant data is never touched - only configuration.
    """
    allocator = LocalIdAllocator()

    file_uploaders = [
        serialize_file_uploader(uploader, allocator, include_blueprints=False)
        for uploader in project.fileuploader_set.all()
    ]
    blueprints = [
        serialize_blueprint(bp, allocator, include_file_uploader_ref=True)
        for bp in project.donationblueprint_set.all()
    ]
    questions = serialize_questions(project, allocator, include_blueprint_ref=True)

    project_data = {field: getattr(project, field) for field in PROJECT_FIELDS}
    project_data["name"] = project.name

    return {
        "schema_version": SCHEMA_VERSION,
        "export_kind": EXPORT_KIND_PROJECT,
        "exported_at": timezone.now().isoformat(),
        "ddm_version": DDM_VERSION,
        "project": project_data,
        "file_uploaders": file_uploaders,
        "blueprints": blueprints,
        "questions": questions,
    }
