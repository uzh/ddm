import json

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from ddm.core.utils.transfer.schema import (
    EXPORT_KIND_BLUEPRINT,
    TransferValidationError,
    validate_envelope,
)
from ddm.datadonation.models import FileUploader


class BlueprintImportUploadForm(forms.Form):
    """
    Uploads and structurally validates a standalone blueprint export file.
    `file_uploader` is scoped to the target project by the view. `clean_file`
    returns the parsed payload's single blueprint dict, ready for
    `build_blueprint()`.
    """

    file = forms.FileField(label="Blueprint export file (.json)")
    file_uploader = forms.ModelChoiceField(
        queryset=FileUploader.objects.none(),
        required=False,
        label="Attach to File Uploader",
        help_text="Optional - leave blank to import the blueprint unattached.",
    )

    def __init__(
        self, *args, file_uploader_queryset: QuerySet | None = None, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        if file_uploader_queryset is not None:
            self.fields["file_uploader"].queryset = file_uploader_queryset

    def clean_file(self) -> dict:
        uploaded = self.cleaned_data["file"]
        try:
            raw = uploaded.read()
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as e:
            msg = "The uploaded file is not valid JSON."
            raise ValidationError(msg) from e

        try:
            validate_envelope(data, expected_kind=EXPORT_KIND_BLUEPRINT)
        except TransferValidationError as e:
            raise ValidationError(e.errors) from e

        return data["blueprints"][0]
