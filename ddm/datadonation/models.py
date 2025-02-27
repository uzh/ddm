import json

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from ddm.auth.models import ProjectAccessToken
from ddm.core.utils.user_content.template import render_user_content
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
    name = models.CharField(max_length=250)
    project = models.ForeignKey('ddm_projects.DonationProject', on_delete=models.CASCADE)
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

    combined_consent = models.BooleanField(
        default=False,
        verbose_name='All-in-one consent',
        help_text='If enabled, participants will be asked to consent to submit '
                  'all uploaded data at once. Otherwise, participant will be asked to '
                  'consent to the submission of the data separately for each blueprint.'
    )

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        """ This model has a post_delete signal processor (see signals.py). """
        super().delete(*args, **kwargs)

    def get_configs(self, participant_data=None):
        blueprints = self.donationblueprint_set.all()
        instructions = self.donationinstruction_set.all()
        configs = {
            'upload_type': self.upload_type,
            'name': self.name,
            'combined_consent': self.combined_consent,
            'blueprints': [bp.get_config() for bp in blueprints],
            'instructions': [{
                'index': i.index,
                'text': i.render(participant_data),
            } for i in instructions]
        }
        return configs

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
            'Name for this File Blueprint. Will be visible to participants, '
            'so pick an informative name (e.g., "Watch History").'
        )
    )
    description = models.TextField(
        null=True,
        help_text=(
            'A description of which kind of data will be extracted by this '
            'Blueprint (e.g., "The title of your watched videos will be '
            'collected together with the time when you watched it."). '
            'Will be visible to participants.'
        )
    )

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
        help_text=(
            'Indicates on which level of the files\' data structure information should be extractet. '
            'If you want to extract information contained on the first level (e.g., {\'field to be extracted\': value}, '
            'you can leave this field empty. If you want to extract data located on a higher level, then you would '
            'provide the path to the parent field of the data you want to extract (e.g., if your json file is structured like this '
            '{\'friends\': {\'real_friends\': [{\'name to extract\': name, \'date to extract\': date}], \'fake friends\': [{\'name\': name, \'date\': date }]}} '
            'and you want to extract the names and dates of real_friends, you would set the extraction root to \'friends.real_friends\'.'
        )
    )

    csv_delimiter = models.CharField(
        max_length=10,
        default="",
        blank=True,
        help_text=(
            'This field allows you to specify the character that separates '
            'values in the expected CSV file (e.g., , ; or \\t).'
            ' If left empty, DDM will try to infer the delimiter from the '
            'file structure.'
        )
    )

    expected_fields = models.TextField(
        null=False,
        blank=False,
        validators=[COMMA_SEPARATED_STRINGS_VALIDATOR],
        help_text=(
            'Put the field names in double quotes (") and separate them '
            'with commas ("Field A", "Field B").'
        )
    )

    expected_fields_regex_matching = models.BooleanField(
        default=False,
        null=False,
        help_text='Select if you use regex expressions in the "Expected fields".'
    )

    file_uploader = models.ForeignKey(
        'FileUploader',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Associated File Uploader',
        help_text=(
            'The File Uploader through which the related file will be uploaded.'
        )
    )
    regex_path = models.TextField(
        null=True,
        blank=True,
        verbose_name='File path',
        help_text=(
            'The path where the file is expected to be located in the uploaded '
            'ZIP folder. You can use Regex to, e.g., add wildcard characters or '
            'to match files in different languages. Consult the documentation '
            'for some examples.'
        )
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ddm_datadonation:blueprints:edit', args=[str(self.project.url_id), str(self.id)])

    def get_slug(self):
        return 'blueprint'

    def get_config(self):
        config = {
            'id': self.pk,
            'name': self.name,
            'description': self.description,
            'format': self.exp_file_format,
            'json_extraction_root': self.json_extraction_root,
            'expected_fields': json.loads("[" + str(self.expected_fields) + "]"),
            'exp_fields_regex_matching': self.expected_fields_regex_matching,
            'fields_to_extract': self.get_fields_to_extract(),
            'regex_path': self.regex_path,
            'filter_rules': self.get_filter_rules(),
            'csv_delimiter': self.csv_delimiter
        }
        return config

    def get_associated_questions(self):
        return self.questionbase_set.all()

    def get_filter_rules(self):
        return [r.get_rule_config() for r in self.processingrule_set.all().order_by('execution_order')]

    def get_fields_to_extract(self):
        fields = set()
        for r in self.processingrule_set.all():
            if r.comparison_operator is None:
                fields.add(r.field)
        return list(fields)

    def process_donation(self, data, participant):
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

    def validate_donation(self, data):
        # Check if all expected fields are in response.
        response_fields = ['consent', 'extracted_data', 'status']
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

    def create_donation(self, data, participant):
        DataDonation.objects.create(
            project=self.project,
            blueprint=self,
            participant=participant,
            consent=data['consent'],
            status=data['status'],
            data=data['extracted_data']
        )
        return


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
        help_text='An informative name for this rule. Only used internally.'
    )

    field = models.TextField(
        null=False,
        blank=False,
        help_text=(
            'The field on which the rule will be applied (just as a string without quotes).'
            'If a field is mentioned in a rule, it will be kept in the data that are sent to the server.'
        )
    )
    regex_field = models.BooleanField(
        default=False,
        null=False,
        help_text='Select if you use a regex expression in the "Field" setting to match a variable.'
    )
    execution_order = models.IntegerField(
        help_text='The order in which the extraction steps are executed.'
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
        help_text='The value against which the data contained in the indicated field will '
                  'be compared according to the selected comparison logic.'
    )
    replacement_value = models.TextField(
        blank=True,
        help_text='Only required for operation "Replace match (regex)".'
    )

    def get_rule_config(self):
        """
        Return a configuration dict for the processing rule:
        {
            'field': 'field_name',
            'comparison_operator': '==' | '!=' | '>' | '<' | '>=' | '<=' |
                                   'regex-delete-match' | ' regex-replace-match'
                                   'regex-delete-row' | None,
            'comparison_value': '123' | Regex-String | None,
            'replacement_value': String
        }
        """
        return {
            'field': self.field,
            'regex_field': self.regex_field,
            'comparison_operator': self.comparison_operator,
            'comparison_value': self.comparison_value,
            'replacement_value': self.replacement_value
        }


class DataDonation(ModelWithEncryptedData):
    project = models.ForeignKey(
        'ddm_projects.DonationProject',
        on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        'DonationBlueprint',
        null=True,
        on_delete=models.SET_NULL
    )
    participant = models.ForeignKey(
        'ddm_participation.Participant',
        on_delete=models.CASCADE
    )
    time_submitted = models.DateTimeField(default=timezone.now)
    consent = models.BooleanField(default=False)
    status = models.JSONField()
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

    def render(self, context=None):
        return render_user_content(self.text, context)
