import datetime
import json
import os
import random
import string

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import RegexValidator, MinValueValidator, MinLengthValidator
from django.db import models
from django.db.models import Avg, F, ImageField
from django.template import Context, Template
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.debug import sensitive_variables

from ddm.models.auth import ProjectAccessToken
from ddm.models.encryption import Encryption, ModelWithEncryptedData
from ddm.models.logs import ExceptionLogEntry, ExceptionRaisers, EventLogEntry


class ResearchProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ddm_research_profile',
    )
    active = models.BooleanField(default=True)
    created = models.DateTimeField('date registered', default=timezone.now)
    ignore_email_restriction = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


def project_header_dir_path(instance, filename):
    return f'project_{instance.pk}/headers/{filename}'


class DonationProject(models.Model):
    # Basic information for internal organization.
    name = models.CharField(
        max_length=50,
        help_text='Project Name - for internal organisation only (can still be changed later).'
    )
    date_created = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        'ResearchProfile',
        related_name='project_owner',
        on_delete=models.SET_NULL,
        null=True
    )

    # Public information.
    contact_information = RichTextField(
        null=True,
        blank=False,
        verbose_name='Contact information',
        help_text=(
            'Please provide the contact information of the person responsible '
            'for the conduction of this study (Name, professional address, e-mail, tel, ...). The contact information will be '
            'accessible for participants during the data donation. The field is mandatory.'
        ),
        config_name='ddm_ckeditor'
    )
    data_protection_statement = RichTextField(
        null=True,
        blank=False,
        verbose_name='Data Protection Statement',
        help_text=(
            'Please provide a data protection statement for your data donation '
            'collection. This should include the purpose for which the data is '
            'collected, how it will be stored, and who will have access to the data. '
            'The field is mandatory.'
        ),
        config_name='ddm_ckeditor'
    )

    # Information affecting participation flow.
    slug = models.SlugField(
        unique=True,
        verbose_name='URL Identifier',
        help_text='Identifier that is included in the URL through which '
                  'participants can access the project '
                  '(e.g, https://root.url/url-identifier).'
    )
    briefing_text = RichTextUploadingField(
        null=True, blank=True,
        verbose_name='Briefing Text',
        config_name='ddm_ckeditor',
        help_text=(
            'This text will be displayed to participants in the first step before '
            'beginning the data donation. Here, you should introduce your study, '
            'who is responsible for the study, provide a quick summary of what '
            'your participants will be asked to do in the next steps, etc.'
        )
    )
    briefing_consent_enabled = models.BooleanField(
        default=False,
        verbose_name='Briefing Consent Mandatory',
        help_text='Enable this option to obtain explicit consent from participant, '
                  'that they want to start the study.'
    )
    briefing_consent_label_yes = models.CharField(max_length=255, blank=True)
    briefing_consent_label_no = models.CharField(max_length=255, blank=True)
    debriefing_text = RichTextUploadingField(
        null=True, blank=True,
        verbose_name='Debriefing Text',
        config_name='ddm_ckeditor',
        help_text='This text will be displayed to participants on the last page '
                  'of the study (i.e., after the data donation and the questionnaire).'
    )

    # Appearance settings.
    img_header_left = ImageField(
        upload_to=project_header_dir_path,
        null=True,
        blank=True,
        verbose_name='Header Image Left'
    )
    img_header_right = ImageField(
        upload_to=project_header_dir_path,
        null=True,
        blank=True,
        verbose_name='Header Image Right'
    )

    # Access settings.
    public_key = models.BinaryField()
    super_secret = models.BooleanField(default=False)

    # Redirect settings.
    redirect_enabled = models.BooleanField(default=False, verbose_name='Redirect enabled')
    redirect_target = models.CharField(
        max_length=2000,
        blank=True,
        verbose_name='Redirect target',
        help_text=mark_safe(
            'Always include <i>http://</i> or <i>https://</i> in the redirect target. '
            'If URL parameter extraction is enabled for this project, you can '
            'include the extracted URL parameters in the redirect target as follows: '
            '"https://redirect.me/?redirectpara=<b>{{participant.data.url_param.URLParameter}}</b>".')
    )

    # URL parameter extraction settings.
    url_parameter_enabled = models.BooleanField(default=False, verbose_name='URL parameter extraction enabled')
    expected_url_parameters = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Expected URL parameter',
        help_text='Separate multiple parameters with a semikolon (";"). '
                  'Semikolons are not allowed as part of the expected url parameters.'
    )

    @sensitive_variables()
    def __init__(self, *args, **kwargs):
        self.secret_key = settings.SECRET_KEY
        if 'secret_key' in kwargs:
            self.secret_key = kwargs['secret_key']
            kwargs.pop('secret_key')
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project-detail', args=[str(self.id)])

    def get_salt(self):
        return str(self.date_created)

    def clean_file_on_reupload(self):
        """
        Deletes previous file on model FileFields or ImageFields if a file
        is re-uploaded.
        """
        i = DonationProject.objects.get(pk=self.pk)
        for field in i._meta.fields:
            if field.get_internal_type() in ['FileField', 'ImageField']:
                if getattr(i, field.name) != getattr(self, field.name):
                    file_attr = getattr(i, field.name)
                    try:
                        if os.path.isfile(file_attr.path):
                            os.remove(file_attr.path)
                    except ValueError:
                        pass
        return

    @sensitive_variables()
    def save(self, *args, **kwargs):
        if not self.pk:
            if self.owner is None:
                raise ValidationError(
                    'DonationProject.owner cannot be null on create.')
        else:
            self.clean_file_on_reupload()

        if not self.public_key:
            self.public_key = Encryption.get_public_key(self.secret, str(self.date_created))
        super().save(*args, **kwargs)

    @property
    def secret(self):
        return self.secret_key

    @secret.setter
    def secret(self, value):
        self.secret_key = value

    def delete(self, using=None, keep_parents=False):
        # Manually delete related questions to circumvent foreign key integrity
        # problem caused by QuestionBase models inheriting from django-polymorphic.
        # (see https://github.com/django-polymorphic/django-polymorphic/issues/34#issuecomment-1027866872)
        for question in self.questionbase_set.all():
            question.delete()
        return super().delete(using, keep_parents)

    def get_statistics(self):
        participants = Participant.objects.filter(project=self)
        statistics = {
            'n_started': participants.count(),
            'n_completed': participants.filter(completed=True).count(),
            'completion_rate': participants.filter(completed=True).count() / participants.count() if participants.count() > 0 else 0,
            'n_donations': DataDonation.objects.filter(project=self, status='success').count(),
            'n_errors': ExceptionLogEntry.objects.filter(project=self).count(),
            'average_time': str(participants.filter(completed=True).aggregate(v=Avg(F('end_time')-F('start_time')))['v']).split(".")[0]
        }
        return statistics

    def get_questionnaire_config(self, participant, view):
        """
        Returns a dictionary containing all information to render the
        questionnaire for a given participant.
        """
        q_config = []
        questions = self.questionbase_set.all().order_by('page', 'index')
        for question in questions:
            if question.is_general():
                q_config.append(question.get_config(participant, view))
            else:
                try:
                    donation = DataDonation.objects.get(
                        blueprint=question.blueprint,
                        participant=participant
                    )
                except ObjectDoesNotExist:
                    msg = ('Questionnaire Rendering Exception: No donation '
                           f'found for participant {participant.pk} and '
                           f'blueprint {question.blueprint.pk}.')
                    ExceptionLogEntry.objects.create(
                        project=self,
                        raised_by=ExceptionRaisers.SERVER,
                        message=msg
                    )
                    continue

                if donation.consent and donation.status == 'success':
                    q_config.append(question.get_config(participant, view))
        return q_config

    def get_expected_url_parameters(self):
        return self.expected_url_parameters.split(';')

    def get_token(self):
        return ProjectAccessToken.objects.filter(project=self).first()

    def create_token(self, expiration_days=None):
        token = self.get_token()
        if token:
            token.delete()
        if expiration_days:
            expiration_date = timezone.now() + datetime.timedelta(days=expiration_days)
        else:
            expiration_date = None
        EventLogEntry.objects.create(
            project=self, description='New Access Token Created')
        return ProjectAccessToken.objects.create(
            project=self, expiration_date=expiration_date)


def get_extra_data_default():
    """ Return default value for Participant.extra_data. """
    return dict(url_param=dict())


def create_asciidigits_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=24))


class Participant(models.Model):
    project = models.ForeignKey('DonationProject', on_delete=models.CASCADE)

    external_id = models.CharField(
        unique=True, null=False,
        max_length=24,
        validators=[MinLengthValidator(24)]
    )

    # Participation statistics.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    current_step = models.IntegerField(blank=True, null=True)

    extra_data = models.JSONField(default=get_extra_data_default)

    def get_context_data(self):
        """
        Returns data that can be accessed when participant is passed to a
        template as a context variable.
        """
        context_data = {
            'public_id': self.external_id,
            'data': self.extra_data,
            'donation_info': self.get_donation_info()
        }
        return context_data

    def get_donation_info(self):
        donations = DataDonation.objects.filter(participant=self)
        donation_info = {
            'n_success': donations.filter(status='success').count(),
            'n_pending': donations.filter(status='pending').count(),
            'n_failed': donations.filter(status='failed').count(),
            'n_no_data_extracted': donations.filter(status='nothing extracted').count()
        }
        return donation_info

    def save(self, *args, **kwargs):
        if self.pk is None:
            new_external_id = create_asciidigits_id()
            while len(Participant.objects.filter(external_id=new_external_id)) != 0:
                new_external_id = create_asciidigits_id()
            self.external_id = new_external_id
        super().save(*args, **kwargs)


class QuestionnaireResponse(ModelWithEncryptedData):
    # Will only ever be deleted, when the project is deleted.
    project = models.ForeignKey('DonationProject', on_delete=models.CASCADE)
    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)
    time_submitted = models.DateTimeField(default=timezone.now)
    data = models.BinaryField()


COMMA_SEPARATED_STRINGS_VALIDATOR = RegexValidator(
    r'^((["][^"]+["]))(\s*,\s*((["][^"]+["])))*[,\s]*$',
    message=(
        'Field must contain one or multiple comma separated strings. '
        'Strings must be enclosed in double quotes ("string").'
    )
)


class FileUploader(models.Model):
    name = models.CharField(max_length=250)
    project = models.ForeignKey('DonationProject', on_delete=models.CASCADE)
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
            'blueprints': [bp.get_config() for bp in blueprints],
            'instructions': [{
                'index': i.index,
                'text': Template(i.text).render(Context({'participant': participant_data}))
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
        'DonationProject',
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
        blank=True
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
        help_text='Select if you use regex expressions in the "Excpected fields".'
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
        return reverse('blueprint-edit', args=[str(self.project_id), str(self.id)])

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

    def get_instructions(self):
        return [{'index': i.index, 'text': i.text} for i in self.donationinstruction_set.all()]

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
                project=self.oproject,
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
        'DonationProject',
        on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        'DonationBlueprint',
        null=True,
        on_delete=models.SET_NULL
    )
    participant = models.ForeignKey(
        'Participant',
        on_delete=models.CASCADE
    )
    time_submitted = models.DateTimeField(default=timezone.now)
    consent = models.BooleanField(default=False)
    status = models.JSONField()
    data = models.BinaryField()


class DonationInstruction(models.Model):
    text = RichTextUploadingField(null=True, blank=True, config_name='ddm_ckeditor')
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
