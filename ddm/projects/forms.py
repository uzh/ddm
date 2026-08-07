import json
from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget

from ddm.projects.models import DonationProject

User = get_user_model()


class ProjectCreateForm(forms.ModelForm):
    project_password = forms.CharField(
        min_length=10, max_length=150, required=False, widget=forms.PasswordInput()
    )
    project_password_confirm = forms.CharField(
        min_length=10, max_length=150, required=False, widget=forms.PasswordInput()
    )

    class Meta:
        model = DonationProject
        fields = [
            "name",
            "slug",
            "super_secret",
            "owner",
            "contact_information",
            "data_protection_statement",
        ]
        widgets = {
            "owner": forms.HiddenInput(),
            "data_protection_statement": CKEditor5Widget(config_name="ddm_ckeditor"),
            "contact_information": CKEditor5Widget(config_name="ddm_ckeditor"),
        }
        labels = {"super_secret": "Enable enhanced encryption"}
        help_texts = {
            "name": 'Visible to participants (e.g., "TikTok Project")',
            "slug": mark_safe(
                "Used in the participant URL (e.g., <code>root.url/"
                '<span class="fw-bold">my-url-identifier</span></code>). '
                "Letters, numbers, hyphens, and underscores only."
            ),
            "contact_information": (
                "Provide contact information of the project lead "
                "(name, professional address, email, tel, ...)"
            ),
            "data_protection_statement": (
                "Provide your data protection statement (purpose of data collection, "
                "how the data will be stored, who has access, retention times etc.)"
            ),
        }

    field_order = [
        "name",
        "slug",
        "super_secret",
        "project_password",
        "project_password_confirm",
        "contact_information",
        "data_protection_statement",
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if "initial" in kwargs:
            self.fields["owner"].initial = kwargs["initial"]["owner"]

    def clean(self) -> dict[str, Any] | None:
        super_secret = self.data.get("super_secret", False)
        secret = self.data.get("project_password", None)
        secret_confirm = self.data.get("project_password_confirm", None)

        if super_secret and secret in ["", None]:
            msg = "Super secret project needs a project password."
            raise ValidationError(msg)

        if super_secret and (secret != secret_confirm):
            msg = "The two supplied project passwords do not match."
            raise ValidationError(msg)

        return super().clean()

    def save(self, commit: bool = True) -> DonationProject:  # noqa: FBT002
        project: DonationProject = super().save(commit=False)
        if project.super_secret:
            project.secret_key = self.data["project_password"]
        project.save()
        return project


class EditPublicInformationForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = [
            "name",
            "slug",
            "active",
            "contact_information",
            "data_protection_statement",
        ]
        widgets = {
            "data_protection_statement": CKEditor5Widget(config_name="ddm_ckeditor"),
            "contact_information": CKEditor5Widget(config_name="ddm_ckeditor"),
        }
        help_texts = {
            "name": 'Visible to participants (e.g., "TikTok Project")',
            "slug": mark_safe(
                "Used in the participant URL (e.g., <code>root.url/"
                '<span class="fw-bold">my-url-identifier</span></code>). '
                "Letters, numbers, hyphens, and underscores only."
            ),
            "contact_information": (
                "Provide contact information of the project lead "
                "(name, professional address, email, tel, ...)"
            ),
            "data_protection_statement": (
                "Provide your data protection statement (purpose of data collection, "
                "how the data will be stored, who has access, retention times etc.)"
            ),
        }


class EditUrlParameterExtractionForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = [
            "url_parameter_enabled",
            "expected_url_parameters",
        ]
        help_texts = {
            "expected_url_parameters": mark_safe(
                "Separate multiple parameters with semicolons "
                "(<code>paramA<b>;</b> paramB</code>) - Semicolons are not "
                "allowed as part of the expected url parameters"
            )
        }

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        url_parameter_enabled = cleaned_data.get("url_parameter_enabled", False)
        expected_url_parameters = cleaned_data.get("expected_url_parameters", "")

        if url_parameter_enabled and not expected_url_parameters:
            self.add_error(
                "expected_url_parameters",
                "URL parameter is enabled but no parameter is defined to be extracted.",
            )
        return cleaned_data


class EditRedirectConfigurationForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = [
            "redirect_enabled",
            "redirect_target",
        ]

        help_texts = {
            "redirect_target": mark_safe(
                "The redirect address must start with <code>https://</code>; "
                "It is possible to pass information to the redirect address "
                "by passing variables to URL parameters: "
                "<code>https://redirect.me/?participantId="
                "<b>{{ participant.public_id }}</b></code>"
            )
        }

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()

        redirect_enabled = cleaned_data.get("redirect_enabled", False)
        redirect_target = cleaned_data.get("redirect_target", "")
        if redirect_enabled and not redirect_target:
            self.add_error(
                "redirect_target",
                "Redirect is enabled but no redirect target is defined.",
            )

        return cleaned_data


class EditBrandingForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = [
            "show_project_title",
            "img_header_left",
            "img_header_right",
        ]
        labels = {
            "img_header_left": "Logo Header Left",
            "img_header_right": "Logo Header Right",
        }
        help_texts = {
            "show_project_title": (
                "If enabled, the project title is shown in the header of the "
                "participation interface."
            ),
        }


class CustomJSONWidget(forms.Textarea):
    """
    Custom widget that formats JSON with indents.
    """

    def format_value(self, value: Any) -> str:  # noqa: ANN401
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=4, ensure_ascii=False)

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return json.dumps(parsed, indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                return value

        return str(value)


class ProjectEditCustomUploaderTranslationsForm(forms.ModelForm):
    def clean_custom_uploader_translations(self) -> Any:  # noqa: ANN401
        value = self.cleaned_data.get("custom_uploader_translations")

        # Handle various "empty" cases
        if value in [None, "", "{}"]:
            return {}

        # If it's already a dict/list, return as-is
        if isinstance(value, (dict, list)):
            return value

        # If it's a string, try to parse it
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return {}
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                msg = "Invalid JSON format"
                raise forms.ValidationError(msg) from e

        return value

    class Meta:
        model = DonationProject
        fields = [
            "custom_uploader_translations",
        ]
        widgets = {
            "custom_uploader_translations": CustomJSONWidget(
                attrs={"class": "w-100", "rows": 25}
            )
        }


class BriefingEditForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = [
            "briefing_text",
            "briefing_consent_enabled",
            "briefing_consent_label_yes",
            "briefing_consent_label_no",
        ]
        widgets = {
            "briefing_text": CKEditor5Widget(config_name="ddm_ckeditor"),
        }
        help_texts = {
            "briefing_text": (
                "Introduce your study, provide a quick summary of what your "
                "participants will be asked to do in the next steps, etc."
            ),
            "briefing_consent_enabled": (
                "If enabled, participants will have to provide explicit "
                "participation consent before they can advance to the data "
                "donation"
            ),
        }
        labels = {
            "briefing_consent_label_yes": "Response Consent",
            "briefing_consent_label_no": "Response Non-Consent",
        }

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()

        consent_enabled = cleaned_data.get("briefing_consent_enabled", False)
        consent_label_yes = cleaned_data.get("briefing_consent_label_yes", "")
        consent_label_no = cleaned_data.get("briefing_consent_label_no", "")
        consent_label_error_msg = (
            "When briefing consent is enabled, a consent label must be provided."
        )

        if consent_enabled and not consent_label_yes:
            self.add_error("briefing_consent_label_yes", consent_label_error_msg)

        if consent_enabled and not consent_label_no:
            self.add_error("briefing_consent_label_no", consent_label_error_msg)
        return cleaned_data


class DebriefingEditForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = ["debriefing_text"]
        widgets = {
            "debriefing_text": CKEditor5Widget(config_name="ddm_ckeditor_temp_func"),
        }
        help_texts = {"debriefing_text": ""}
