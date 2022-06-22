from ckeditor.fields import RichTextField

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from ddm.models import Encryption


class ResearchProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ddm_research_profile',
    )
    active = models.BooleanField(default=True)
    created = models.DateTimeField('date registered', default=timezone.now)
    ignore_email_restriction = models.BooleanField(default=False)
    api_key = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True
    )
    api_secret = models.CharField(
        max_length=64,
        null=True,
        blank=True
    )  # This is a hash of the one-time key.


class DonationProject(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(
        verbose_name='External Project Slug',
        unique=True
    )
    intro_text = RichTextField(
        null=True,
        blank=True,
        verbose_name='Welcome Page Text'
    )
    outro_text = RichTextField(
        null=True,
        blank=True,
        verbose_name='End Page Text'
    )

    date_created = models.DateTimeField(default=timezone.now)

    secret_key = settings.SECRET_KEY
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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.owner is None:
                raise ValidationError(
                    'DonationProject.owner cannot be null on create.')
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


@receiver(pre_save, sender=DonationProject)
def my_callback(sender, instance, *args, **kwargs):
    if not instance.public_key:
        instance.public_key = Encryption(
            instance.secret_key, str(instance.date_created)).public_key
        instance.super_secret = True


class Participant(models.Model):
    project = models.ForeignKey(
        DonationProject,
        on_delete=models.CASCADE
    )

    # Participation statistics.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)


class QuestionnaireResponse(models.Model):
    # Will only ever be deleted, when the project is deleted.
    project = models.ForeignKey(
        DonationProject,
        on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE
    )
    time_submitted = models.DateTimeField(default=timezone.now)
    data = models.BinaryField()

    def save(self, *args, **kwargs):
        self.data = Encryption(
            public_key=self.project.public_key
        ).encrypt(self.data)
        super().save(*args, **kwargs)

    def get_decrypted_data(self, secret=None):
        if not secret:
            decrypted_data = Encryption(
                secret=settings.SECRET_KEY,
                salt=str(self.project.date_created)
            ).decrypt(self.data)
        else:
            decrypted_data = Encryption(
                secret=secret,
                salt=str(self.project.date_created)
            ).decrypt(self.data)
        return decrypted_data
