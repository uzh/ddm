from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from pydantic import ValidationError as PydanticValidationError

from ddm.core.utils.user_content.template import render_user_content
from ddm.core.utils.validators import validate_regex_pattern, validate_safe_regex
from ddm.datadonation.schemas import (
    CSVParserConfig,
    FileParserConfigAdapter,
    JSONParserConfig,
    TXTParserConfig,
)
from ddm.datadonation.utils import count_data_entries
from ddm.encryption.models import ModelWithEncryptedData
from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers

if TYPE_CHECKING:
    from django.utils.safestring import SafeString

    from ddm.participation.models import Participant


COMMA_SEPARATED_STRINGS_VALIDATOR = RegexValidator(
    r'^((["][^"]+["]))(\s*,\s*((["][^"]+["])))*[,\s]*$',
    message=(
        "Field must contain one or multiple comma separated strings. "
        'Strings must be enclosed in double quotes ("string").'
    ),
)


class FileUploader(models.Model):
    project = models.ForeignKey(
        "ddm_projects.DonationProject", on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=250,
        help_text="Internal name for this File Uploader",
        blank=False,
    )

    display_name = models.CharField(
        max_length=250,
        help_text="Public name of the File Uploader (displayed to participants)",
    )
    index = models.PositiveIntegerField()

    class UploadTypes(models.TextChoices):
        ZIP_FILE = "zip file"
        SINGLE_FILE = "single file"

    upload_type = models.CharField(
        max_length=20,
        choices=UploadTypes.choices,
        default=UploadTypes.SINGLE_FILE,
        verbose_name="Upload type",
    )

    extract_nested_zips = models.BooleanField(default=False)
    extraction_depth = models.PositiveIntegerField(default=0)

    combined_consent = models.BooleanField(
        default=False,
        verbose_name="All-in-one consent",
        help_text="If enabled, participants provide consent once for all data",
    )

    class Meta:
        ordering = ["index", "pk"]

    def __str__(self) -> str:
        return f"{self.name} ({self.upload_type})"

    def save(self, *args, **kwargs) -> None:
        if self.index is None:
            uploader_indices = self.project.fileuploader_set.all().values_list(
                "index", flat=True
            )
            self.index = 1 if not uploader_indices else max(uploader_indices) + 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """This model has a post_delete signal processor (see signals.py)."""
        return super().delete(*args, **kwargs)


class DonationBlueprint(models.Model):
    project = models.ForeignKey(
        "ddm_projects.DonationProject", on_delete=models.CASCADE
    )
    file_uploader = models.ForeignKey(
        "FileUploader",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Associated File Uploader",
        help_text="The File Uploader through which the related file will be uploaded",
    )
    name = models.CharField(
        max_length=250, help_text="Internal name for this File Blueprint"
    )
    description = models.TextField(
        blank=True, help_text="Blueprint description visible for participants"
    )
    display_name = models.CharField(
        max_length=250,
        help_text="Public name of the blueprint (displayed to participants)",
    )
    display_position = models.PositiveIntegerField(default=1)

    class FileFormats(models.TextChoices):
        JSON_FORMAT = "json", "JSON file"
        CSV_FORMAT = "csv", "CSV file"
        TXT_FORMAT = "txt", "TXT file"

    exp_file_format = models.CharField(
        max_length=10,
        choices=FileFormats.choices,
        default=FileFormats.JSON_FORMAT,
        verbose_name="Expected file format",
    )

    parser_config = models.JSONField()

    expected_fields = models.TextField(
        null=False,
        blank=False,
        validators=[COMMA_SEPARATED_STRINGS_VALIDATOR],
        help_text=(
            'Comma-separated, in double quotes: <code>"Field A", "Field B"</code>'
        ),
    )

    expected_fields_regex_matching = models.BooleanField(
        default=False,
        null=False,
        help_text='Select if you use regex expressions in the "Expected fields"',
    )

    nested_expected_fields = models.TextField(
        blank=True,
        default="",
        validators=[COMMA_SEPARATED_STRINGS_VALIDATOR],
        help_text=(
            'Comma-separated, in double quotes: <code>"Field A", "Field B"</code>. '
            "Only used if a Nested loop path is configured (JSON format)."
        ),
        verbose_name="Nested expected fields",
    )

    nested_expected_fields_regex_matching = models.BooleanField(
        default=False,
        null=False,
        help_text='Select if you use regex expressions in the "Nested expected fields"',
    )

    backup_for = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="backups",
        help_text=(
            "If set, this blueprint is used as a fallback when the referenced "
            "blueprint's parser fails to extract data (either because it does "
            "not find the expected file or because it encounters an error)."
        ),
    )
    backup_priority = models.PositiveIntegerField(
        default=0,
        help_text=(
            "If a Blueprint has multiple backups, backup blueprints with lower "
            "priority values are tried first when the main blueprint's parser fails."
        ),
    )

    regex_path = models.TextField(
        blank=True,
        validators=[validate_regex_pattern],
        verbose_name="File path",
        help_text=(
            "The path where the file is expected to be located in the uploaded "
            "ZIP folder. You can use Regex to, e.g., add wildcard characters or "
            "to match files in different languages. Consult the documentation "
            "for some examples."
        ),
    )  # TODO: Deprecate in future major release v4; replaced by FilePath model.

    class Meta:
        ordering = ["display_position", "pk"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse(
            "ddm_datadonation:blueprints:edit",
            args=[str(self.project.url_id), str(self.id)],
        )

    @property
    def is_backup(self) -> bool:
        return self.backup_for_id is not None

    def clean(self) -> None:
        errors = {}

        self.clean_parser_config(errors)
        self.clean_backup_config(errors)
        self.clean_expected_fields_regex(errors)
        self.clean_nested_expected_fields(errors)

        if errors:
            raise ValidationError(errors)

        super().clean()

    def clean_parser_config(self, errors: dict) -> None:
        try:
            FileParserConfigAdapter.validate_python(self.parser_config)
        except PydanticValidationError as e:
            errors["parser_config"] = str(e)

    def clean_backup_config(self, errors: dict) -> None:
        if self.backup_for_id is None:
            return

        if self.pk is not None and self.backup_for_id == self.pk:
            errors["backup_for"] = "A blueprint cannot be a backup for itself."
            return

        if self.backup_for.backup_for_id is not None:
            errors["backup_for"] = (
                "A backup blueprint cannot itself have a backup. Select a "
                "primary blueprint (one that is not already a backup)."
            )
            return

        if self.backup_for.project_id != self.project_id:
            errors["backup_for"] = (
                "A backup blueprint must belong to the same project as the "
                "blueprint it backs up."
            )

    def clean_expected_fields_regex(self, errors: dict) -> None:
        """Validate expected_fields as regex patterns when regex matching is enabled."""
        if not (self.expected_fields_regex_matching and self.expected_fields):
            return
        self._validate_regex_patterns(self.expected_fields, "expected_fields", errors)

    def clean_nested_expected_fields(self, errors: dict) -> None:
        """Validate nested_expected_fields configuration.

        nested_expected_fields is only meaningful when the blueprint is JSON
        format and has a nested_loop_path configured; also validates its
        entries as regex patterns when nested regex matching is enabled.
        """
        if self.nested_expected_fields:
            if self.exp_file_format != self.FileFormats.JSON_FORMAT:
                errors["nested_expected_fields"] = (
                    "Nested expected fields require the file format to be JSON."
                )
            elif not (self.parser_config or {}).get("nested_loop_path", ""):
                errors["nested_expected_fields"] = (
                    "Nested expected fields require a Nested loop path to be "
                    "configured."
                )

        if self.nested_expected_fields_regex_matching and self.nested_expected_fields:
            self._validate_regex_patterns(
                self.nested_expected_fields, "nested_expected_fields", errors
            )

    @staticmethod
    def _validate_regex_patterns(raw_value: str, error_key: str, errors: dict) -> None:
        """Parse a comma-separated quoted-string field and validate each
        entry as a safe regex pattern."""
        # Parse the comma-separated quoted strings: "pattern1", "pattern2"
        try:
            patterns = json.loads("[" + raw_value + "]")
        except json.JSONDecodeError:
            return  # Existing COMMA_SEPARATED_STRINGS_VALIDATOR handles format errors

        for pattern in patterns:
            try:
                validate_safe_regex(pattern)
            except ValidationError as e:
                errors[error_key] = f"Invalid regex in pattern '{pattern}': {e.message}"
                break

    def get_parser_config(self) -> CSVParserConfig | JSONParserConfig | TXTParserConfig:
        return FileParserConfigAdapter.validate_python(self.parser_config)

    @staticmethod
    def get_slug() -> str:
        return "blueprint"

    def process_donation(self, data: dict, participant: Participant) -> None:
        if self.validate_donation(data):
            self.create_donation(data, participant)
        else:
            msg = (
                "Data Donation Processing Exception: Donation validation "
                f"failed for blueprint {self.pk}"
            )
            ExceptionLogEntry.objects.create(
                project=self.project,
                blueprint=self,
                raised_by=ExceptionRaisers.SERVER,
                message=msg,
            )

    def validate_donation(self, data: dict) -> bool:
        # Check if all expected fields are in response.
        response_fields = ["consent", "extractedData", "status"]
        if not all(k in data for k in response_fields):
            msg = (
                "Data Donation Processing Exception: Donation data for "
                f"Donation Blueprint {self.pk} does not contain the "
                f"expected information. Expected fields: {response_fields}; "
                f"Present fields: {data.keys()}."
            )
            ExceptionLogEntry.objects.create(
                project=self.project,
                blueprint=self,
                raised_by=ExceptionRaisers.SERVER,
                message=msg,
            )
            return False

        return True

    def create_donation(self, data: dict, participant: Participant) -> None:
        DataDonation.objects.create(
            project=self.project,
            blueprint=self,
            participant=participant,
            consent=data["consent"],
            data_extraction_state=data["status"],
            data=data["extractedData"],
            n_data_entries=count_data_entries(data["extractedData"]),
        )


class BlueprintFilePath(models.Model):
    blueprint = models.ForeignKey(
        "DonationBlueprint",
        null=False,
        on_delete=models.CASCADE,
    )

    path = models.TextField()
    is_regex = models.BooleanField(default=False)

    priority = models.IntegerField(default=1)

    class Meta:
        ordering = ["priority", "path"]

    def __str__(self) -> str:
        return self.path

    def clean(self) -> None:
        """Validate regex pattern."""

        errors = {}
        # Validate path when regex is enabled
        if self.path and self.is_regex:
            try:
                validate_safe_regex(self.path)
            except ValidationError as e:
                errors["path"] = f"Invalid regex in pattern file path: {e.message}"

        if errors:
            raise ValidationError(errors)

        super().clean()


class ExtractionField(models.Model):
    class Scope(models.TextChoices):
        ROOT = "root", "Root level"
        NESTED = "nested", "Nested level"

    blueprint = models.ForeignKey(
        "DonationBlueprint",
        null=False,
        on_delete=models.CASCADE,
    )
    scope = models.CharField(
        max_length=10,
        choices=Scope.choices,
        default=Scope.ROOT,
        help_text=(
            "Whether this field is extracted from the top-level item, or "
            "from a nested sub-item (only relevant when a Nested loop path "
            "is set)."
        ),
    )
    expected_name = models.TextField(
        blank=False,
        help_text=(
            "The name of the field to extract, as it appears in the file. "
            "To reach a value nested inside another field, separate the "
            "names with a dot, e.g. <code>message.author.role</code>. This "
            "only works when Regex is switched off."
        ),
    )
    match_regex = models.BooleanField(default=False)
    keep_in_donation = models.BooleanField(default=False)
    alias = models.CharField(
        max_length=125,
        blank=True,
        help_text=(
            "Optional internal name to store this field under, esp. useful when "
            "`expected name` is a regex pattern and you want a clean field name "
            "in the stored data structure rather than the value defined in "
            "`expected name`."
        ),
    )

    def __str__(self) -> str:
        return self.get_name()

    def clean(self) -> None:
        errors = {}

        # Validate expected_fields when regex matching is enabled
        if self.match_regex and self.expected_name:
            try:
                validate_safe_regex(self.expected_name)
            except ValidationError as e:
                errors["expected_name"] = f"Invalid regex: {e.message}"

        if self.scope == self.Scope.NESTED and self.blueprint_id:
            blueprint = self.blueprint
            if blueprint.exp_file_format != blueprint.FileFormats.JSON_FORMAT:
                errors["scope"] = (
                    "Nested-scope fields require the blueprint's file format "
                    "to be JSON."
                )
            elif not (blueprint.parser_config or {}).get("nested_loop_path", ""):
                errors["scope"] = (
                    "Nested-scope fields require the blueprint to have a "
                    "Nested loop path configured."
                )

        if errors:
            raise ValidationError(errors)

        super().clean()

    def get_name(self) -> str:
        if self.alias not in ["", None]:
            return self.alias
        return self.expected_name


# TODO: Rename to ExtractionRule
class ProcessingRule(models.Model):
    """
    A processing rule that defines how the data uploaded to VUE will be processed
    before being sent to the server.
    Generates a JSON configuration that is passed to the VUE frontend component
    'UploaderApp'.
    """

    blueprint = models.ForeignKey(
        "DonationBlueprint", null=False, blank=False, on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=250, help_text="A label for this rule (internal use only)"
    )

    field = models.ForeignKey(
        "ExtractionField",
        null=True,
        on_delete=models.SET_NULL,
    )

    execution_order = models.IntegerField(
        help_text="The order in which rules are applied"
    )

    class ComparisonOperators(models.TextChoices):
        EQUAL = "==", "Equal (==)"
        NOT_EQUAL = "!=", "Not Equal (!=)"
        GREATER = ">", "Greater than (>)"
        SMALLER = "<", "Smaller than (<)"
        GREATER_OR_EQUAL = ">=", "Greater than or equal (>=)"
        SMALLER_OR_EQUAL = "<=", "Smaller than or equal (<=)"
        REGEX_DELETE_MATCH = "regex-delete-match", "Delete match (regex)"
        REGEX_REPLACE_MATCH = "regex-replace-match", "Replace match (regex)"
        REGEX_DELETE_ROW = "regex-delete-row", "Delete row when match (regex)"

    comparison_operator = models.CharField(
        max_length=24,
        choices=ComparisonOperators.choices,
        verbose_name="Extraction Operator",
    )
    comparison_value = models.TextField(
        blank=True, help_text="The value to compare the field against"
    )
    replacement_value = models.TextField(
        blank=True, help_text='Only required for operation "Replace match (regex)"'
    )

    def __str__(self) -> str:
        return f"Processing rule {self.pk}"

    def clean(self) -> None:
        regex_operators = [
            self.ComparisonOperators.REGEX_DELETE_MATCH,
            self.ComparisonOperators.REGEX_REPLACE_MATCH,
            self.ComparisonOperators.REGEX_DELETE_ROW,
        ]

        errors = {}

        if self.comparison_operator in regex_operators and self.comparison_value:
            try:
                validate_safe_regex(self.comparison_value)
            except ValidationError as e:
                errors["comparison_value"] = f"Invalid regex: {e.message}"

        if errors:
            raise ValidationError(errors)

        super().clean()


class DataDonation(ModelWithEncryptedData):
    project = models.ForeignKey(
        "ddm_projects.DonationProject", on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        "DonationBlueprint",
        null=True,
        on_delete=models.SET_NULL,
        # TODO: Set this to a different policy; not very intuitive
    )
    participant = models.ForeignKey(
        "ddm_participation.Participant", on_delete=models.CASCADE
    )
    time_submitted = models.DateTimeField(default=timezone.now)
    consent = models.BooleanField(default=False, null=True)
    status = models.JSONField(null=True)
    # Status is replaced by data_extraction_state in v3.0.0 -
    #  TODO: deprecate in future release

    data = models.BinaryField()

    class DataExtractionState(models.TextChoices):
        DATA_EXTRACTED = "DATA_EXTRACTED"
        NO_DATA_EXTRACTED = "NO_DATA_EXTRACTED"
        NOT_ATTEMPTED = "NOT_ATTEMPTED"
        FAILED = "FAILED"

    data_extraction_state = models.CharField(
        max_length=24,
        choices=DataExtractionState.choices,
        blank=True,
        default="",
    )

    n_data_entries = models.IntegerField(null=True)


class DonationInstruction(models.Model):
    text = models.TextField()
    index = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    file_uploader = models.ForeignKey(
        "FileUploader",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name="Associated File Uploader",
    )

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(
                fields=["index", "file_uploader"], name="unique_index_per_file_uploader"
            ),
        ]

    def __str__(self) -> str:
        return f"Donation Instruction {self.pk}"

    # TODO: Refactor this function - too complex.
    def save(self, *args, **kwargs) -> None:  # noqa: C901, PLR0912
        if kwargs.pop("ignore_index_check", False):
            return super().save()

        if self.pk:
            initial_index = DonationInstruction.objects.get(pk=self.pk).index
        else:
            initial_index = None
        index_taken = (
            self.file_uploader.donationinstruction_set.filter(index=self.index)
            .exclude(pk=self.pk)
            .exists()
        )
        if index_taken and (self.index != initial_index):
            # Account for unique constraint by doing a "proxy"-save to free index.
            target_index = self.index
            self.index = self.file_uploader.donationinstruction_set.count() + 5
            super().save()

            # Change indices of involved objects:
            queryset = self.file_uploader.donationinstruction_set.exclude(pk=self.pk)
            if initial_index is None:
                queryset = queryset.filter(index__gte=target_index).order_by("-index")
                for q in queryset:
                    q.index += 1
                for q in queryset:
                    q.save(ignore_index_check=True)
            elif target_index < initial_index:
                queryset = queryset.filter(
                    index__gte=target_index, index__lt=initial_index
                ).order_by("-index")
                for q in queryset:
                    q.index += 1
                for q in queryset:
                    q.save(ignore_index_check=True)
            elif target_index > initial_index:
                queryset = queryset.filter(
                    index__gt=initial_index, index__lte=target_index
                ).order_by("index")
                for q in queryset:
                    q.index -= 1
                for q in queryset:
                    q.save(ignore_index_check=True)

            # Revert "proxy"-save.
            self.index = target_index
            return super().save()

        return super().save()

    def clean(self) -> None:
        # Ensure that index of instruction page is not greater than
        #  the set of existing instructions + 1.
        n_instructions = self.file_uploader.donationinstruction_set.all().count()
        if self.pk:
            if self.index > n_instructions:
                msg = f"Index must be in range 1 to {n_instructions}."
                raise ValidationError(msg)
        elif self.index > (n_instructions + 1):
            msg = f"Index must be in range 1 to {n_instructions + 1}."
            raise ValidationError(msg)
        super().clean()

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """This model has a post_delete signal processor (see signals.py)."""
        return super().delete(*args, **kwargs)

    def render(self, context: dict | None = None) -> SafeString:
        return render_user_content(self.text, context)
