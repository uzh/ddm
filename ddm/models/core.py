import json
import logging

from ckeditor.fields import RichTextField

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, F
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

import ddm.models.exceptions as ddm_exceptions
from ddm.models.encryption import Encryption, ModelWithEncryptedData


from rest_framework.authtoken.models import Token


logger = logging.getLogger(__name__)


class ResearchProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ddm_research_profile',
    )
    active = models.BooleanField(default=True)
    created = models.DateTimeField('date registered', default=timezone.now)
    ignore_email_restriction = models.BooleanField(default=False)

    def get_token(self):
        return Token.objects.filter(user=self.user).first()

    def create_token(self):
        token = self.get_token()
        if token:
            token.delete()
        return Token.objects.create(user=self.user)


class DonationProject(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, verbose_name='External Project Slug')
    intro_text = RichTextField(null=True, blank=True, verbose_name='Welcome Page Text')
    outro_text = RichTextField(null=True, blank=True, verbose_name='End Page Text')
    contact_information = RichTextField(null=True, blank=False, verbose_name='Contact information')
    data_protection_statement = RichTextField(null=True, blank=False, verbose_name='Data Protection Statement')

    date_created = models.DateTimeField(default=timezone.now)

    public_key = models.BinaryField()
    super_secret = models.BooleanField(default=False)

    redirect_enabled = models.BooleanField(default=False, verbose_name='Redirect enabled')
    redirect_target = models.CharField(
        max_length=2000,
        null=True, blank=True,
        verbose_name='Redirect target',
        help_text=mark_safe(
            'Always include <i>http://</i> or <i>https://</i> in the redirect target. '
            'If URL parameter extraction is enabled for this project, you can '
            'include the extracted URL parameters in the redirect target as follows: '
            '"https://redirect.me/?redirectpara=<b>{{URLParameter}}</b>".')
    )

    url_parameter_enabled = models.BooleanField(default=False, verbose_name='URL parameter extraction enabled')
    expected_url_parameters = models.CharField(
        max_length=500,
        null=True, blank=True,
        verbose_name='Expected URL parameter',
        help_text='Separate multiple parameters with a semikolon (";"). '
                  'Semikolons are not allowed as part of the expected url parameters.'
    )

    owner = models.ForeignKey(
        'ResearchProfile',
        related_name='project_owner',
        on_delete=models.SET_NULL,
        null=True
    )
    collaborators = models.ManyToManyField(
        'ResearchProfile',
        related_name='project_collaborators'
    )

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

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.owner is None:
                raise ValidationError(
                    'DonationProject.owner cannot be null on create.')

            if self.super_secret:
                self.public_key = Encryption(self.secret, str(self.date_created)).public_key
        else:
            if self.owner in self.collaborators.all():
                raise ValidationError(
                    'DonationProject.owner cannot be a collaborator at the same time.')
        super().save(*args, **kwargs)

    @property
    def secret(self):
        return self.secret_key

    @secret.setter
    def secret(self, value):
        self.secret_key = value

    def get_statistics(self):
        participants = Participant.objects.filter(project=self)
        statistics = {
            'n_started': participants.count(),
            'n_completed': participants.filter(completed=True).count(),
            'completion_rate': participants.filter(completed=True).count() / participants.count() if participants.count() > 0 else 0,
            'n_donations': DataDonation.objects.filter(project=self).count(),
            'n_errors': ddm_exceptions.ExceptionLogEntry.objects.filter(project=self).count(),
            'average_time': str(participants.filter(completed=True).aggregate(v=Avg(F('end_time')-F('start_time')))['v']).split(".")[0]
        }
        return statistics

    def get_expected_url_parameters(self):
        return self.expected_url_parameters.split(';')


def get_extra_data_default():
    """ Return default value for Participant.extra_data. """
    return dict(url_param=dict())


class Participant(models.Model):
    project = models.ForeignKey('DonationProject', on_delete=models.CASCADE)

    # Participation statistics.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)

    extra_data = models.JSONField(default=get_extra_data_default)


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


class BlueprintContainer(models.Model):
    name = models.CharField(max_length=250)
    project = models.ForeignKey(
        'DonationProject',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    def get_slug(self):
        return 'blueprint-container'

    def get_absolute_url(self):
        return reverse('blueprint-container-edit', args=[str(self.project_id), str(self.id)])

    def get_blueprints(self):
        blueprints = DonationBlueprint.objects.filter(blueprint_container=self)
        return blueprints

    def get_configs(self):
        bp_configs = []
        blueprints = self.get_blueprints()
        for bp in blueprints:
            bp_configs.append(bp.get_config())
        return bp_configs

    def get_instructions(self):
        return [{'index': i.index, 'text': i.text} for i in self.donationinstruction_set.all()]


# TODO: For admin section: Add validation on save to ensure that regex_path != None when blueprint_container != None
class DonationBlueprint(models.Model):
    project = models.ForeignKey(
        'DonationProject',
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=250)

    class FileFormats(models.TextChoices):
        JSON_FORMAT = 'json'
        # CSV_FORMAT = 'csv',
        # HTML_FORMAT = 'html',
        # XLSX_FORMAT = 'xlsx',

    exp_file_format = models.CharField(
        max_length=10,
        choices=FileFormats.choices,
        default=FileFormats.JSON_FORMAT,
        verbose_name='Expected file format',
    )

    expected_fields = models.TextField(
        null=False,
        blank=False,
        validators=[COMMA_SEPARATED_STRINGS_VALIDATOR],
        help_text='Put the field names in double quotes (") and separate them with commas ("Field A", "Field B").'
    )

    # Configuration if related to BlueprintContainer:
    blueprint_container = models.ForeignKey(
        'BlueprintContainer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Blueprint container',
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
            'filter_rules': self.get_filter_rules()
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
            logger.error(f'Donation not processed by blueprint {self.pk}')
        return

    @staticmethod
    def validate_donation(data):
        # Check if all expected fields are in response.
        response_fields = ['consent', 'extracted_data', 'status']
        if not all(k in data for k in response_fields):
            logger.error(
                'Donation data does not contain the expected information. '
                f'Expected key: {response_fields}; '
                f'Present fields: {data.keys()}.'
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

    # TODO: inclusive = models.BooleanField()  # Option to include or exclude data points, when there is an error in the operation.

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
    status = models.JSONField()
    data = models.BinaryField()


# TODO: Outsource to separate model.py file when instruction database is added.
class DonationInstruction(models.Model):
    text = RichTextField(null=True, blank=True, config_name='ddm_ckeditor')
    index = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    blueprint = models.ForeignKey(
        'DonationBlueprint',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    blueprint_container = models.ForeignKey(
        'BlueprintContainer',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['index']
        constraints = [
            models.UniqueConstraint(
                fields=['index', 'blueprint'],
                name='unique_index_per_blueprint'
            ),
            models.UniqueConstraint(
                fields=['index', 'blueprint_container'],
                name='unique_index_per_container'
            ),
        ]

    def get_query_object(self):
        if self.blueprint:
            query_object = self.blueprint
        else:
            query_object = self.blueprint_container
        return query_object

    def clean(self):
        # Ensure that instruction is correctly linked to one blueprint type.
        if not self.blueprint and not self.blueprint_container:
            raise ValidationError(
                'Must be linked to either a DonationBlueprint or a BlueprintContainer.'
            )
        if self.blueprint and self.blueprint_container:
            raise ValidationError(
                'Must be linked to either a DonationBlueprint or '
                'a BlueprintContainer, but not both.'
            )

        # Ensure that index of instruction page is not greater than set of existing instructions + 1.
        n_instructions = self.get_query_object().donationinstruction_set.count()
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
        index_taken = self.get_query_object().donationinstruction_set.filter(index=self.index).exclude(pk=self.pk).exists()
        if index_taken and (self.index != initial_index):

            # Account for unique constraint by doing a "proxy"-save to free index.
            target_index = self.index
            self.index = self.get_query_object().donationinstruction_set.count() + 5
            super().save()

            # Change indices of involved objects:
            queryset = self.get_query_object().donationinstruction_set.exclude(pk=self.pk)
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
