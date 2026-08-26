import json

from django import forms
from django.core.exceptions import ValidationError

from ddm.core.utils.transfer.schema import (
    EXPORT_KIND_QUESTIONNAIRE,
    TransferValidationError,
    validate_envelope,
)


class QuestionnaireImportUploadForm(forms.Form):
    """
    Uploads and structurally validates a standalone questionnaire export
    file. `clean_file` returns the parsed payload's question list, ready
    for `build_questions()`.
    """

    file = forms.FileField(label="Questionnaire export file (.json)")

    def clean_file(self) -> list:
        uploaded = self.cleaned_data["file"]
        try:
            raw = uploaded.read()
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as e:
            msg = "The uploaded file is not valid JSON."
            raise ValidationError(msg) from e

        try:
            validate_envelope(data, expected_kind=EXPORT_KIND_QUESTIONNAIRE)
        except TransferValidationError as e:
            raise ValidationError(e.errors) from e

        return data["questions"]
