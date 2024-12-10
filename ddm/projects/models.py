import datetime
import os

from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.db.models import Avg, F, ImageField
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.debug import sensitive_variables

from ddm.auth.models import ProjectAccessToken
from ddm.core.utils.misc import create_asciidigits_id
from ddm.datadonation.models import DataDonation
from ddm.encryption.models import Encryption
from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers, EventLogEntry
from ddm.participation.models import Participant


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
    url_id = models.SlugField(unique=True, max_length=8)

    # Basic information for internal organization.
    name = models.CharField(
        max_length=50,
        help_text=(
            'Project Name - for internal organisation only (can still be '
            'changed later).'
        )
    )

    # Note: Value of "date_created" attribute must not be changed after
    # instance creation as it is used for en-/decryption.
    date_created = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        'ResearchProfile',
        related_name='project_owner',
        on_delete=models.SET_NULL,
        null=True
    )

    # Public information.
    contact_information = models.TextField(
        blank=False,
        verbose_name='Contact information',
        help_text=(
            'Please provide the contact information of the person responsible '
            'for the conduction of this study (Name, professional address, e-mail, '
            'tel, ...). The contact information will be accessible for '
            'participants during the data donation. The field is mandatory.'
        )
    )
    data_protection_statement = models.TextField(
        blank=False,
        verbose_name='Data Protection Statement',
        help_text=(
            'Please provide a data protection statement for your data donation '
            'collection. This should include the purpose for which the data is '
            'collected, how it will be stored, and who will have access to the '
            'data. The field is mandatory.'
        ),
    )

    # Information affecting participation flow.
    slug = models.SlugField(
        unique=True,
        verbose_name='URL Identifier',
        help_text='Identifier that is included in the URL through which '
                  'participants can access the project '
                  '(e.g, https://root.url/url-identifier). Can only contain '
                  'letters, hyphens, numbers or underscores.'
    )
    briefing_text = models.TextField(
        blank=False,
        verbose_name='Briefing Text',
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
    debriefing_text = models.TextField(
        blank=False,
        verbose_name='Debriefing Text',
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
        verbose_name='Redirect address',
        help_text=mark_safe(
            'Always include <i>http://</i> or <i>https://</i> in the redirect address. '
            'If URL parameter extraction is enabled for this project, you can '
            'include the extracted URL parameters in the redirect address as follows: '
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

    active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Participants can only take part in a project if it is active.'
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
        return reverse('ddm_projects:detail', args=[str(self.url_id)])

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

        if not self.url_id:
            self.url_id = create_asciidigits_id(8)
            while DonationProject.objects.filter(url_id=self.url_id).exists():
                self.url_id = create_asciidigits_id(8)

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
            'completion_rate': self.get_completion_rate(participants),
            'n_donations': DataDonation.objects.filter(project=self, status='success').count(),
            'n_errors': ExceptionLogEntry.objects.filter(project=self).count(),
            'average_time': self.get_average_completion_time(participants),
        }
        return statistics

    def get_completion_rate(self, participants=None):
        if participants is None:
            participants = Participant.objects.filter(project=self)
        if participants.count() > 0:
            return participants.filter(completed=True).count() / participants.count()
        else:
            return 0

    def get_average_completion_time(self, participants=None):
        if participants is None:
            participants = Participant.objects.filter(project=self)
        return str(participants.filter(completed=True).aggregate(
            v=Avg(F('end_time') - F('start_time')))['v']).split(".")[0]

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
