from typing import Any

from django import forms
from django.db.models import QuerySet
from django.forms import Textarea, inlineformset_factory
from django.utils.safestring import mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget
from pydantic import ValidationError as PydanticValidationError
from pydantic_core import PydanticUndefined

from ddm.datadonation.models import (
    BlueprintFilePath,
    DonationBlueprint,
    DonationInstruction,
    ExtractionField,
    FileUploader,
    ProcessingRule,
)
from ddm.datadonation.schemas import CSVParserConfig, JSONParserConfig, TXTParserConfig

# Maps Django form field names -> Pydantic schema field names, per format.
FIELD_NAME_MAP: dict[str, dict[str, str]] = {
    "json": {
        "json_extraction_root": "extraction_root",
        "json_nested_loop_path": "nested_loop_path",
        "json_array_join_separator": "array_join_separator",
    },
    "csv": {
        "csv_delimiter": "delimiter",
    },
    "txt": {
        "txt_record_separator": "record_separator",
        "txt_field_separator": "field_separator",
        "txt_kv_separator": "kv_separator",
        "txt_skip_header_lines": "skip_header_lines",
        "txt_skip_footer_lines": "skip_footer_lines",
        "txt_ignore_blank_lines": "ignore_blank_lines",
        "txt_trim_whitespace": "trim_whitespace",
    },
}

CONFIG_CLASSES: dict[str, type] = {
    "json": JSONParserConfig,
    "csv": CSVParserConfig,
    "txt": TXTParserConfig,
}


def _schema_default(model_cls, field_name: str, fallback: Any = "") -> Any:  # noqa: ANN001, ANN401
    default = model_cls.model_fields[field_name].default
    return fallback if default is PydanticUndefined else default


def _unescape(value: str) -> str:
    """Convert literal escape sequences typed by the user (\\n, \\t) into
    their real character equivalents (actual newline, actual tab)."""
    return value.replace("\\n", "\n").replace("\\t", "\t")


def _escape(value: str) -> str:
    """Inverse of _unescape: convert real control characters back into
    their literal escape-sequence text, for display in a text input."""
    return value.replace("\n", "\\n").replace("\t", "\\t")


class BlueprintForm(forms.ModelForm):
    # --- JSON-specific ---
    json_extraction_root = forms.CharField(
        max_length=200,
        required=False,
        label="Extraction Root",
        help_text=mark_safe(
            "Optional: if the data you want isn't at the top level of the "
            "file, enter the field name that contains it here. Leave empty "
            "to extract straight from the top level. To reach a field "
            "nested inside another field, separate the names with a dot, "
            "e.g. <code>friends.real_friends</code>."
        ),
    )
    json_nested_loop_path = forms.CharField(
        max_length=200,
        required=False,
        label="Nested loop path",
        help_text=mark_safe(
            "Optional: use this if each item contains a list (or a named "
            "set) of related sub-items that you also want to extract as "
            "their own rows &mdash; for example, if each conversation "
            "contains a set of messages. Enter the field name that holds "
            "these sub-items (e.g. <code>messages</code>). Each sub-item "
            "becomes a separate row, and the data extracted from the "
            "parent item is automatically included in every row. To reach "
            "a field nested inside another field, separate the names with "
            "a dot, e.g. <code>data.messages</code>."
        ),
    )
    json_array_join_separator = forms.CharField(
        max_length=20,
        required=False,
        initial="\n",
        label="Array join separator",
        help_text=mark_safe(
            "If an extracted field contains several separate values (e.g. "
            "multiple lines of a message) instead of a single value, they "
            "are combined into one text using this separator. Use "
            "<code>\\n</code> to join them with a line break."
        ),
    )

    # --- CSV-specific ---
    csv_delimiter = forms.CharField(
        max_length=10,
        required=False,
        help_text=mark_safe(
            "The character that separates values in the CSV "
            "(e.g., <code>,</code> <code>;</code> or <code>\\t</code> for tab). "
            "If left empty, the delimiter is inferred automatically."
        ),
    )

    # --- TXT-specific ---
    txt_record_separator = forms.CharField(
        max_length=20,
        required=False,
        initial="\n\n",
        label="Record/entry separator",
        help_text=mark_safe(
            "The character(s) that separate one entry from the next in the "
            "file &mdash; for example, a blank line or a single line "
            "break. Use <code>\\n</code> for a line break, or "
            "<code>\\n\\n</code> for a blank line between entries."
        ),
    )
    txt_field_separator = forms.CharField(
        max_length=20,
        required=False,
        initial="\n",
        label="Field separator",
        help_text=mark_safe(
            "The character sequence that separates individual fields within a single "
            "record (e.g., a line break if each field is on its own line). "
            "Use <code>\\n</code> for a line break."
        ),
    )
    txt_kv_separator = forms.CharField(
        max_length=10,
        required=False,
        initial=":",
        label="Key-value separator",
        help_text=mark_safe(
            "The character that separates a field's name from its value within a line "
            "(e.g., <code>:</code> in <code>Name: John</code>, or <code>=</code> in "
            "<code>name=John</code>)."
        ),
    )
    txt_skip_header_lines = forms.IntegerField(
        required=False,
        initial=0,
        min_value=0,
        label="Skip header lines",
        help_text="How many lines to skip at the beginning of the TXT-file.",
    )
    txt_skip_footer_lines = forms.IntegerField(
        required=False,
        initial=0,
        min_value=0,
        label="Skip footer lines",
        help_text="How many lines to skip at the end of the TXT-file.",
    )
    txt_ignore_blank_lines = forms.BooleanField(
        required=False,
        initial=True,
        label="Ignore blank lines",
    )
    txt_trim_whitespace = forms.BooleanField(
        required=False,
        initial=True,
        label="Trim whitespace",
        help_text=(
            "Whether to trim whitespace around records/entries and key-value pairs."
        ),
    )

    class Meta:
        model = DonationBlueprint
        fields = [
            "name",
            "display_name",
            "description",
            "display_position",
            "exp_file_format",
            "file_uploader",
            "expected_fields",
            "expected_fields_regex_matching",
            "nested_expected_fields",
            "nested_expected_fields_regex_matching",
            "backup_for",
            "backup_priority",
        ]
        widgets = {
            "expected_fields": forms.Textarea(attrs={"rows": 1}),
            "nested_expected_fields": forms.Textarea(attrs={"rows": 1}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "expected_fields_regex_matching": "Expected fields use regex matching",
            "nested_expected_fields_regex_matching": (
                "Nested expected fields use regex matching"
            ),
            "display_position": "Display order",
        }
        help_texts = {
            "name": 'For internal use (e.g., "watch_history")',
            "display_name": (
                'Title of the Blueprint shown to participants (e.g., "Watch History").'
            ),
            "display_position": (
                "Controls display order in Blueprint list. Lower = first."
            ),
            "description": (
                "Explains to participants what data is extracted "
                '(e.g., "Videos you watched and when")'
            ),
            "expected_fields": mark_safe(
                'Comma-separated, in double quotes: <code>"Field A", "Field B"</code>'
            ),
            "expected_fields_regex_matching": "",
            "nested_expected_fields": mark_safe(
                'Comma-separated, in double quotes: <code>"Field A", "Field B"</code>. '
                "Only used if a Nested loop path is configured (JSON format)."
            ),
            "nested_expected_fields_regex_matching": "",
        }

    def __init__(self, *args, **kwargs) -> None:
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        if self.project and not self.instance.pk:
            self.instance.project = self.project

        self.populate_format_specific_fields()

        if "backup_for" in self.fields:
            self.fields["backup_for"].queryset = self.get_backup_queryset()
            self.fields["backup_for"].error_messages["invalid_choice"] = (
                "The selected blueprint must use the same file uploader "
                "as this blueprint (or is not eligible as a backup)."
            )

    def populate_format_specific_fields(self) -> None:
        """Populates format-specific fields from the stored parser_config."""
        config = getattr(self.instance, "parser_config", None) or {}
        fmt = config.get("format") or (
            self.instance.exp_file_format if self.instance.pk else ""
        )

        config_class = CONFIG_CLASSES.get(fmt)
        if config_class is None:
            return

        field_map = FIELD_NAME_MAP.get(fmt, {})

        for form_field, schema_field in field_map.items():
            fallback = _schema_default(config_class, schema_field)
            raw_value = config.get(schema_field, fallback)
            self.fields[form_field].initial = (
                _escape(raw_value) if isinstance(raw_value, str) else raw_value
            )

    def get_backup_queryset(self) -> QuerySet[DonationBlueprint]:
        file_uploader = self._get_effective_file_uploader()
        if file_uploader is None:
            return DonationBlueprint.objects.none()

        queryset = DonationBlueprint.objects.filter(
            backup_for__isnull=True, file_uploader=file_uploader
        )

        if self.project:
            queryset = queryset.filter(project=self.project)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        return queryset

    def _get_effective_file_uploader(self) -> None | FileUploader:
        """The FileUploader that should govern backup_for choices: the
        submitted value on a bound form, falling back to the instance's
        current value otherwise (e.g. on initial GET)."""
        if self.is_bound:
            uploader_id = self.data.get(self.add_prefix("file_uploader"))
            if uploader_id:
                return FileUploader.objects.filter(pk=uploader_id).first()
            return None
        return self.instance.file_uploader

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if cleaned_data is None:
            return cleaned_data

        self._clean_name(cleaned_data)
        self._clean_parser_config(cleaned_data)
        return cleaned_data

    def _clean_name(self, cleaned_data: dict[str, Any]) -> None:
        name = cleaned_data.get("name")

        if name and self.project:
            qs = DonationBlueprint.objects.filter(name=name, project=self.project)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                msg = (
                    "A Blueprint with this name already exists "
                    "in this project. Please choose another one."
                )
                self.add_error("name", msg)

    def _clean_parser_config(self, cleaned_data: dict[str, Any]) -> None:
        fmt = cleaned_data.get("exp_file_format")
        config_class = CONFIG_CLASSES.get(fmt)
        field_map = FIELD_NAME_MAP.get(fmt, {})

        if config_class is None:
            self.add_error("exp_file_format", "Unsupported file format.")
            return

        # form_field -> schema_field, so build raw_config keyed by schema_field.
        raw_config = {
            schema_field: (
                _unescape(cleaned_data.get(form_field))
                if isinstance(cleaned_data.get(form_field), str)
                else cleaned_data.get(form_field)
            )
            for form_field, schema_field in field_map.items()
            if cleaned_data.get(form_field) not in (None, "")
        }

        try:
            config = config_class(**raw_config)
        except PydanticValidationError as e:
            # Map errors to specific form fields.
            reverse_map = {v: k for k, v in field_map.items()}
            for error in e.errors():
                schema_field = error["loc"][0]
                form_field = reverse_map.get(schema_field)
                if form_field:
                    self.add_error(form_field, error["msg"])
                else:
                    self.add_error(None, error["msg"])
            return

        dumped_config = config.model_dump()
        cleaned_data["parser_config"] = dumped_config
        self.instance.parser_config = dumped_config

    def save(self, commit: bool = True) -> DonationBlueprint:  # noqa: FBT002
        self.instance.parser_config = self.cleaned_data["parser_config"]
        return super().save(commit=commit)


class InstructionsForm(forms.ModelForm):
    class Meta:
        model = DonationInstruction
        fields = ["index", "text"]
        widgets = {
            "text": CKEditor5Widget(config_name="ddm_ckeditor"),
        }

        labels = {
            "index": "Page number",
        }


class ExtractionFieldForm(forms.ModelForm):
    class Meta:
        model = ExtractionField
        fields = [
            "scope",
            "expected_name",
            "match_regex",
            "keep_in_donation",
            "alias",
        ]
        widgets = {
            "expected_name": Textarea(attrs={"cols": 60, "rows": 1}),
        }
        labels = {"alias": "Rename to", "scope": "Scope"}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Don't let the model's non-empty `default` become this field's
        # form-level `initial`: for an unsaved/"extra" formset row, a
        # non-empty initial no longer matches the empty submitted data of
        # an untouched row, which defeats the formset's "skip untouched
        # extra rows" (has_changed) logic and breaks required-field
        # validation for every other field on that row.
        if not self.instance.pk:
            self.fields["scope"].initial = ""


ExtractionFieldInlineFormset = inlineformset_factory(
    DonationBlueprint, ExtractionField, form=ExtractionFieldForm, extra=0
)


class ProcessingRuleForm(forms.ModelForm):
    class Meta:
        model = ProcessingRule
        fields = [
            "execution_order",
            "name",
            "field",
            "comparison_operator",
            "comparison_value",
            "replacement_value",
        ]
        widgets = {
            "comparison_value": Textarea(attrs={"cols": 60, "rows": 1}),
            "replacement_value": Textarea(attrs={"cols": 60, "rows": 1}),
        }
        help_texts = {
            "replacement_value": "The replacement for matched text.",
        }

    def __init__(
        self, *args, blueprint: DonationBlueprint | None = None, **kwargs
    ) -> None:
        """Limit field queryset to ExtractionFields belonging to same blueprint."""
        super().__init__(*args, **kwargs)

        blueprint = blueprint or getattr(self.instance, "blueprint", None)

        if blueprint is not None:
            self.fields["field"].queryset = ExtractionField.objects.filter(
                blueprint=blueprint
            )
        else:
            self.fields["field"].queryset = ExtractionField.objects.none()


ProcessingRuleInlineFormset = inlineformset_factory(
    DonationBlueprint, ProcessingRule, form=ProcessingRuleForm, extra=0
)


class SecretInputForm(forms.Form):
    secret = forms.CharField(widget=forms.PasswordInput())


class FileUploaderForm(forms.ModelForm):
    class Meta:
        model = FileUploader
        fields = [
            "display_name",
            "name",
            "upload_type",
            "extract_nested_zips",
            "extraction_depth",
            "combined_consent",
            "index",
        ]
        labels = {
            "extract_nested_zips": "Extract nested zip files",
            "extraction_depth": "Extraction depth",
            "combined_consent": "All-in-one consent",
            "index": "Display position",
        }
        widgets = {
            "extraction_depth": forms.NumberInput(),
        }
        help_texts = {
            "name": 'For internal use (e.g., "tiktok_uploader")',
            "display_name": (
                "Title of the Uploader shown to participants "
                '(e.g., "TikTok Data Donation")'
            ),
            "combined_consent": "",
            "index": (
                "Controls display order when multiple Uploaders exist. Lower = first."
            ),
            "extract_nested_zips": (
                "When enabled, any zip files found inside the uploaded zip "
                "are automatically extracted up to the extraction depth "
                "so their contents can be processed by Blueprints."
            ),
            "extraction_depth": (
                "Levels of nested zips to extract (0 = top-level only)"
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        name = cleaned_data.get("name")

        if name and self.project:
            qs = FileUploader.objects.filter(name=name, project=self.project)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                msg = (
                    "A File Uploader with this name already exists "
                    "in this project. Please choose another one."
                )
                self.add_error("name", msg)

        return cleaned_data


class BlueprintFilePathForm(forms.ModelForm):
    class Meta:
        model = BlueprintFilePath
        fields = [
            "path",
            "is_regex",
            "priority",
        ]
        widgets = {
            "path": Textarea(attrs={"cols": 60, "rows": 1}),
        }
        labels = {
            "path": "File path",
        }


BlueprintFilePathInlineFormset = inlineformset_factory(
    DonationBlueprint, BlueprintFilePath, form=BlueprintFilePathForm, extra=0
)
