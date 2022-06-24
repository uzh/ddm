from ckeditor.fields import RichTextField

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from ddm.models import Encryption, ModelWithEncryptedData

from rest_framework.authtoken.models import Token


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

    date_created = models.DateTimeField(default=timezone.now)

    public_key = models.BinaryField()
    super_secret = models.BooleanField(default=False)

    owner = models.ForeignKey(
        ResearchProfile,
        related_name='project_owner',
        on_delete=models.SET_NULL,
        null=True
    )
    collaborators = models.ManyToManyField(
        ResearchProfile,
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


class Participant(models.Model):
    project = models.ForeignKey(DonationProject, on_delete=models.CASCADE)

    # Participation statistics.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)


class QuestionnaireResponse(ModelWithEncryptedData):
    # Will only ever be deleted, when the project is deleted.
    project = models.ForeignKey(DonationProject, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    time_submitted = models.DateTimeField(default=timezone.now)
    data = models.BinaryField()
