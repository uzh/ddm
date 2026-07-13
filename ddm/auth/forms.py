from typing import Any

from django import forms
from django.core.exceptions import ValidationError


class TokenCreationForm(forms.Form):
    expiration_days = forms.IntegerField(
        initial=30,
        min_value=1,
        max_value=90,
        required=False,
    )
    action = forms.CharField(
        max_length=20, initial="create", widget=forms.HiddenInput()
    )

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        action = cleaned_data.get("action")

        if action == "create" and not cleaned_data.get("expiration_days"):
            msg = "Expiration days required when creating token."
            raise ValidationError(msg)

        return cleaned_data
