import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from ddm.core.utils.transfer.schema import (
    EXPORT_KIND_PROJECT,
    TransferValidationError,
    validate_envelope,
)
from ddm.projects.models import DonationProject, ResearchProfile


class ProjectImportUploadForm(forms.Form):
    """
    Step 1 of project import: upload + structurally validate the export
    file. `clean_file` returns the parsed payload dict (not the raw file),
    ready to be handed to `build_project()` once the user has reviewed the
    project name/slug in step 2.
    """

    file = forms.FileField(label="Project export file (.json)")

    def clean_file(self) -> dict:
        uploaded = self.cleaned_data["file"]
        try:
            raw = uploaded.read()
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as e:
            msg = "The uploaded file is not valid JSON."
            raise ValidationError(msg) from e

        try:
            validate_envelope(data, expected_kind=EXPORT_KIND_PROJECT)
        except TransferValidationError as e:
            raise ValidationError(e.errors) from e

        return data


class ProjectNameSlugReviewForm(forms.Form):
    """
    Shared review step for both project import (step 2) and in-app project
    copy: lets the user confirm/edit the new project's name and URL
    identifier before it's created, rather than silently auto-suffixing a
    participant-facing slug. `include_owner_field` is only set for
    superusers, letting them pick a different target owner.
    """

    name = forms.CharField(
        max_length=50,
        help_text='Visible to participants (e.g., "TikTok Project")',
    )
    slug = forms.SlugField(
        help_text=mark_safe(
            "Used in the participant URL (e.g., <code>root.url/"
            '<span class="fw-bold">my-url-identifier</span></code>). '
            "Letters, numbers, hyphens, and underscores only."
        )
    )
    owner = forms.ModelChoiceField(
        queryset=ResearchProfile.objects.all(), required=True
    )

    def __init__(self, *args, include_owner_field: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not include_owner_field:
            del self.fields["owner"]

    def clean_slug(self) -> str:
        slug = self.cleaned_data["slug"]
        if DonationProject.objects.filter(slug=slug).exists():
            msg = "A project with this URL identifier already exists."
            raise ValidationError(msg)
        return slug
