import datetime
import json
import os
import random
import string

from ckeditor.fields import RichTextField

from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import RegexValidator, MinValueValidator, MinLengthValidator
from django.db import models
from django.db.models import Avg, F, ImageField
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


def project_header_dir_path(instance, filename):
    return f'project_{instance.pk}/headers/{filename}'


class DonationProject(models.Model):
    # Basic information for internal organization.
    name = models.CharField(max_length=50)
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
            'for the conduction of this study. The contact information will be '
            'accessible for participants during the data donation.'
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
            'collected, how it will be stored, and who will have access to the data.'
        ),
        config_name='ddm_ckeditor'
    )

    # Information affecting participation flow.
    slug = models.SlugField(unique=True, verbose_name='External Project Slug')
    briefing_text = RichTextField(
        null=True, blank=True,
        verbose_name='Welcome Page Text',
        config_name='ddm_ckeditor'
    )
    briefing_consent_enabled = models.BooleanField(default=False)
    briefing_consent_label_yes = models.CharField(max_length=255, blank=True)
    briefing_consent_label_no = models.CharField(max_length=255, blank=True)
    debriefing_text = RichTextField(
        null=True, blank=True,
        verbose_name='End Page Text',
        config_name='ddm_ckeditor'
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
            '"https://redirect.me/?redirectpara=<b>{{URLParameter}}</b>".')
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
            'n_donations': DataDonation.objects.filter(project=self).count(),
            'n_errors': ExceptionLogEntry.objects.filter(project=self).count(),
            'average_time': str(participants.filter(completed=True).aggregate(v=Avg(F('end_time')-F('start_time')))['v']).split(".")[0]
        }
        return statistics

    def get_questionnaire_config(self, participant, view):
        """
        Returns a dictionary containing all information to render the
        questionnaire for a given participant.
        """
        q_config = {}
        questions = self.questionbase_set.all()
        for question in questions:
            if question.is_general():
                q_config[question.pk] = question.get_config(participant, view)
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

                if donation.consent:
                    q_config[question.pk] = question.get_config(participant, view)
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

    extra_data = models.JSONField(default=get_extra_data_default)

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

    def get_configs(self):
        configs = {
            'upload_type': self.upload_type,
            'name': self.name,
            'blueprints': [bp.get_config() for bp in self.donationblueprint_set.all()],
            'instructions': [{'index': i.index, 'text': i.text} for i in self.donationinstruction_set.all()]
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
    name = models.CharField(max_length=250)

    class FileFormats(models.TextChoices):
        JSON_FORMAT = 'json'
        CSV_FORMAT = 'csv'
        # HTML_FORMAT = 'html',
        # XLSX_FORMAT = 'xlsx',

    exp_file_format = models.CharField(
        max_length=10,
        choices=FileFormats.choices,
        default=FileFormats.JSON_FORMAT,
        verbose_name='Expected file format',
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
        help_text='Put the field names in double quotes (") and separate them with commas ("Field A", "Field B").'
    )

    file_uploader = models.ForeignKey(
        'FileUploader',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Associated File Uploader',
    )
    regex_path = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blueprint-edit', args=[str(self.project_id), str(self.id)])

    def get_slug(self):
        return 'blueprint'

    def get_config(self):
        # TODO: Change 'f_expected' and 'f_extract' to something more meaningful
        config = {
            'id': self.pk,
            'name': self.name,
            'format': self.exp_file_format,
            'f_expected': json.loads("[" + str(self.expected_fields) + "]"),
            'f_extract': self.get_fields_to_extract(),
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

        # TODO: Add other validation steps? - e.g., validation of extracted fields
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
    A processing rule that is executed on the specified blueprint field,
    during the file upload in vue.
    Filters or matches values.
    TODO: Improve this description.
    """
    blueprint = models.ForeignKey(
        'DonationBlueprint',
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=250)

    field = models.TextField(null=False, blank=False)
    execution_order = models.IntegerField()

    class ComparisonOperators(models.TextChoices):
        EQUAL = '==', 'Equal (==)'
        NOT_EQUAL = '!=', 'Not Equal (!=)'
        GREATER = '>', 'Greater than (>)'
        SMALLER = '<', 'Smaller than (<)'
        GREATER_OR_EQUAL = '>=', 'Greater than or equal (>=)'
        SMALLER_OR_EQUAL = '<=', 'Smaller than or equal (<=)'
        REGEX = 'regex', 'Regex (removes matches)'

    comparison_operator = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=ComparisonOperators.choices,
        default=None
    )
    comparison_value = models.TextField(blank=True)

    def get_rule_config(self):
        """
        Return a configuration dict for the processing rule:
        {
            'field': 'field_name',
            'comparison_operator': '==' | '!=' | '>' | '<' | '>=' | '<=' | 'regex' | None,
            'comparison_value': '123' | Regex-String | None
        }
        """
        return {
            'field': self.field,
            'comparison_operator': self.comparison_operator,
            'comparison_value': self.comparison_value
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
    status = models.JSONField()  # 'success' if data was successfully donated; 'pending' otherwise
    data = models.BinaryField()


# TODO: Outsource to separate model.py file when instruction database is added.
class DonationInstruction(models.Model):
    text = RichTextField(null=True, blank=True, config_name='ddm_ckeditor')
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

        # TODO: Optimize and prettify the following part:
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
