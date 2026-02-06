import json

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import SafeString

from ddm.auth.models import ProjectAccessToken
from ddm.core.utils.user_content.template import render_user_content
from ddm.core.utils.validators import validate_regex_pattern, validate_safe_regex
from ddm.encryption.models import ModelWithEncryptedData
from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers, EventLogEntry


COMMA_SEPARATED_STRINGS_VALIDATOR = RegexValidator(
    r'^((["][^"]+["]))(\s*,\s*((["][^"]+["])))*[,\s]*$',
    message=(
        'Field must contain one or multiple comma separated strings. '
        'Strings must be enclosed in double quotes ("string").'
    )
)


class FileUploader(models.Model):
    project = models.ForeignKey(
        'ddm_projects.DonationProject',
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=250,
        help_text=(
            'Internal name for this File Uploader'
        ),
        blank=False,
    )

    display_name = models.CharField(
        max_length=250,
        help_text='Public name of the File Uploader (displayed to participants)'
    )
    index = models.PositiveIntegerField()

    class UploadTypes(models.TextChoices):
        ZIP_FILE = 'zip file'
        SINGLE_FILE = 'single file'

    upload_type = models.CharField(
        max_length=20,
        choices=UploadTypes.choices,
        default=UploadTypes.SINGLE_FILE,
        verbose_name='Upload type',
    )

    extract_nested_zips = models.BooleanField(default=False)
    extraction_depth = models.PositiveIntegerField(default=0)

    combined_consent = models.BooleanField(
        default=False,
        verbose_name='All-in-one consent',
        help_text='If enabled, participants provide consent once for all data'
    )

    class Meta:
        ordering = ['index', 'pk']

    def __str__(self):
        return f"{self.name} ({self.upload_type})"

    def delete(self, *args, **kwargs):
        """ This model has a post_delete signal processor (see signals.py). """
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.index is None:
            uploader_indices = self.project.fileuploader_set.all().values_list('index', flat=True)
            self.index = 1 if not uploader_indices else max(uploader_indices) + 1
        super().save(*args, **kwargs)


class DonationBlueprint(models.Model):
    project = models.ForeignKey(
        'ddm_projects.DonationProject',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=250,
        help_text=(
            'Internal name for this File Blueprint'
        )
    )
    description = models.TextField(
        null=True,
        help_text='Blueprint description visible for participants'
    )
    display_name = models.CharField(
        max_length=250,
        help_text='Public name of the blueprint (displayed to participants)'
    )
    display_position = models.PositiveIntegerField(default=1)

    class FileFormats(models.TextChoices):
        JSON_FORMAT = 'json', 'JSON file'
        CSV_FORMAT = 'csv', 'CSV file'
        # HTML_FORMAT = 'html',
        # XLSX_FORMAT = 'xlsx',

    exp_file_format = models.CharField(
        max_length=10,
        choices=FileFormats.choices,
        default=FileFormats.JSON_FORMAT,
        verbose_name='Expected file format',
    )

    json_extraction_root = models.CharField(
        max_length=200,
        default='',
        blank=True,
        verbose_name='Extraction Root',
        help_text='The level in the data structure from which to extract. (optional)'
    )

    csv_delimiter = models.CharField(
        max_length=10,
        default="",
        blank=True,
        help_text=(
            'The character that separates values in the CSV'
        )
    )

    expected_fields = models.TextField(
        null=False,
        blank=False,
        validators=[COMMA_SEPARATED_STRINGS_VALIDATOR],
        help_text=(
            'Comma-separated, in double quotes: <code>"Field A", "Field B"</code>'
        )
    )

    expected_fields_regex_matching = models.BooleanField(
        default=False,
        null=False,
        help_text='Select if you use regex expressions in the "Expected fields"'
    )

    file_uploader = models.ForeignKey(
        'FileUploader',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Associated File Uploader',
        help_text=(
            'The File Uploader through which the related file will be uploaded'
        )
    )
    regex_path = models.TextField(
        null=True,
        blank=True,
        validators=[validate_regex_pattern],
        verbose_name='File path',
        help_text=(
            'The path where the file is expected to be located in the uploaded '
            'ZIP folder. You can use Regex to, e.g., add wildcard characters or '
            'to match files in different languages. Consult the documentation '
            'for some examples.'
        )
    )  # TODO: Deprecate in future major release; replaced by FilePath model.

    class Meta:
        ordering = ['display_position', 'pk']

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('ddm_datadonation:blueprints:edit', args=[str(self.project.url_id), str(self.id)])

    def clean(self):

        errors = {}

        # Validate expected_fields when regex matching is enabled
        if self.expected_fields_regex_matching and self.expected_fields:
            # Parse the comma-separated quoted strings: "pattern1", "pattern2"
            try:
                patterns = json.loads('[' + self.expected_fields + ']')
                for i, pattern in enumerate(patterns):
                    try:
                        validate_safe_regex(pattern)
                    except ValidationError as e:
                        errors['expected_fields'] = f'Invalid regex in pattern "{pattern}": {e.message}'
                        break
            except json.JSONDecodeError:
                pass  # Let the existing COMMA_SEPARATED_STRINGS_VALIDATOR handle format errors

        if errors:
            raise ValidationError(errors)

        super().clean()

    def get_slug(self) -> str:
        return 'blueprint'

    def process_donation(self, data, participant) -> None:
        if self.validate_donation(data):
            self.create_donation(data, participant)
        else:
            msg = ('Data Donation Processing Exception: Donation validation '
                   f'failed for blueprint {self.pk}')
            ExceptionLogEntry.objects.create(
                project=self.project,
                blueprint=self,
                raised_by=ExceptionRaisers.SERVER,
                message=msg
            )
        return

    def validate_donation(self, data) -> bool:
        # Check if all expected fields are in response.
        response_fields = ['consent', 'extractedData', 'status']
        if not all(k in data for k in response_fields):
            msg = ('Data Donation Processing Exception: Donation data for '
                   f'Donation Blueprint {self.pk} does not contain the '
                   f'expected information. Expected fields: {response_fields}; '
                   f'Present fields: {data.keys()}.')
            ExceptionLogEntry.objects.create(
                project=self.project,
                blueprint=self,
                raised_by=ExceptionRaisers.SERVER,
                message=msg
            )
            return False

        return True

    def create_donation(self, data, participant) -> None:
        DataDonation.objects.create(
            project=self.project,
            blueprint=self,
            participant=participant,
            consent=data['consent'],
            status=data['status'],
            data=data['extractedData']
        )
        return


class BlueprintFilePath(models.Model):
    blueprint = models.ForeignKey(
        'DonationBlueprint',
        null=False,
        on_delete=models.CASCADE,
    )

    path = models.TextField()
    is_regex = models.BooleanField(default=False)

    priority = models.IntegerField(default=1)

    class Meta:
        ordering = ['priority', 'path']

    def clean(self):
        """Validate regex pattern."""

        errors = {}
        # Validate path when regex is enabled
        if self.path and self.is_regex:
            try:
                validate_safe_regex(self.path)
            except ValidationError as e:
                errors['path'] = f'Invalid regex in pattern file path: {e.message}'

        if errors:
            raise ValidationError(errors)

        super().clean()


class ProcessingRule(models.Model):
    """
    A processing rule that defines how the data uploaded to VUE will be processed
    before being sent to the server.
    Generates a json configuration that is passed to the VUE frontend component
    'UploaderApp'.
    """
    blueprint = models.ForeignKey(
        'DonationBlueprint',
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=250,
        help_text='A label for this rule (internal use only)'
    )

    field = models.TextField(
        null=False,
        blank=False,
        help_text='The field this rule applies to (without quotes)'
    )
    regex_field = models.BooleanField(
        default=False,
        null=False,
        help_text='Enable if the field name above is a regex pattern'
    )
    execution_order = models.IntegerField(
        help_text='The order in which rules are applied'
    )

    class ComparisonOperators(models.TextChoices):
        EMPTY = '', 'Keep Field'
        EQUAL = '==', 'Equal (==)'
        NOT_EQUAL = '!=', 'Not Equal (!=)'
        GREATER = '>', 'Greater than (>)'
        SMALLER = '<', 'Smaller than (<)'
        GREATER_OR_EQUAL = '>=', 'Greater than or equal (>=)'
        SMALLER_OR_EQUAL = '<=', 'Smaller than or equal (<=)'
        REGEX_DELETE_MATCH = 'regex-delete-match', 'Delete match (regex)'
        REGEX_REPLACE_MATCH = 'regex-replace-match', 'Replace match (regex)'
        REGEX_DELETE_ROW = 'regex-delete-row', 'Delete row when match (regex)'

    comparison_operator = models.CharField(
        max_length=24,
        blank=True,
        null=True,
        choices=ComparisonOperators.choices,
        default=None,
        verbose_name='Extraction Operator'
    )
    comparison_value = models.TextField(
        blank=True,
        help_text='The value to compare the field against'
    )
    replacement_value = models.TextField(
        blank=True,
        help_text='Only required for operation "Replace match (regex)"'
    )

    def clean(self):
        regex_operators = [
            self.ComparisonOperators.REGEX_DELETE_MATCH,
            self.ComparisonOperators.REGEX_REPLACE_MATCH,
            self.ComparisonOperators.REGEX_DELETE_ROW,
        ]

        errors = {}

        # Validate expected_fields when regex matching is enabled
        if self.regex_field and self.field:
            try:
                validate_safe_regex(self.field)
            except ValidationError as e:
                errors['field'] = f'Invalid regex: {e.message}'

        if self.comparison_operator in regex_operators and self.comparison_value:
            try:
                validate_safe_regex(self.comparison_value)
            except ValidationError as e:
                errors['comparison_value'] = f'Invalid regex: {e.message}'

        if errors:
            raise ValidationError(errors)

        super().clean()


class DataDonation(ModelWithEncryptedData):
    project = models.ForeignKey(
        'ddm_projects.DonationProject',
        on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        'DonationBlueprint',
        null=True,
        on_delete=models.SET_NULL  # TODO: Set this to a different policy; not very intuitive
    )
    participant = models.ForeignKey(
        'ddm_participation.Participant',
        on_delete=models.CASCADE
    )
    time_submitted = models.DateTimeField(default=timezone.now)
    consent = models.BooleanField(default=False, null=True)
    status = models.JSONField()  # TODO: Change this to a CHOICE filed or similar (attention: also affects other parts of the code)
    data = models.BinaryField()


class DonationInstruction(models.Model):
    text = models.TextField()
    index = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    file_uploader = models.ForeignKey(
        'FileUploader',
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name='Associated File Uploader',
    )

    class Meta:
        ordering = ['index']
        constraints = [
            models.UniqueConstraint(
                fields=['index', 'file_uploader'],
                name='unique_index_per_file_uploader'
            ),
        ]

    def clean(self):
        # Ensure that index of instruction page is not greater than set of existing instructions + 1.
        n_instructions = self.file_uploader.donationinstruction_set.all().count()
        if self.pk:
            if self.index > n_instructions:
                raise ValidationError(
                    f'Index must be in range 1 to {n_instructions}.'
                )
        else:
            if self.index > (n_instructions + 1):
                raise ValidationError(
                    f'Index must be in range 1 to {n_instructions + 1}.'
                )
        super().clean()

    def save(self, *args, **kwargs):
        if kwargs.pop('ignore_index_check', False):
            return super().save()

        initial_index = DonationInstruction.objects.get(pk=self.pk).index if self.pk else None
        index_taken = self.file_uploader.donationinstruction_set.filter(index=self.index).exclude(pk=self.pk).exists()
        if index_taken and (self.index != initial_index):

            # Account for unique constraint by doing a "proxy"-save to free index.
            target_index = self.index
            self.index = self.file_uploader.donationinstruction_set.count() + 5
            super().save()

            # Change indices of involved objects:
            queryset = self.file_uploader.donationinstruction_set.exclude(pk=self.pk)
            if initial_index is None:
                queryset = queryset.filter(index__gte=target_index).order_by('-index')
                for q in queryset:
                    q.index += 1
                for q in queryset:
                    q.save(ignore_index_check=True)
            elif target_index < initial_index:
                queryset = queryset.filter(index__gte=target_index, index__lt=initial_index).order_by('-index')
                for q in queryset:
                    q.index += 1
                for q in queryset:
                    q.save(ignore_index_check=True)
            elif target_index > initial_index:
                queryset = queryset.filter(index__gt=initial_index, index__lte=target_index).order_by('index')
                for q in queryset:
                    q.index -= 1
                for q in queryset:
                    q.save(ignore_index_check=True)

            # Revert "proxy"-save.
            self.index = target_index
            return super().save()

        return super().save()

    def delete(self, *args, **kwargs):
        """ This model has a post_delete signal processor (see signals.py). """
        super().delete(*args, **kwargs)

    def render(self, context=None) -> SafeString:
        return render_user_content(self.text, context)
