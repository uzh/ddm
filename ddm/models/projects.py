from django.urls import reverse
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver

from ddm.models import Encryption


class DonationProject(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(
        verbose_name='External Project Slug',
        unique=True
    )
    intro_text = RichTextField(null=True, blank=True, verbose_name="Welcome Page Text")
    outro_text = RichTextField(null=True, blank=True, verbose_name="End Page Text")

    date_created = models.DateTimeField(default=timezone.now)

    secret_key = settings.SECRET_KEY
    public_key = models.BinaryField()
    super_secret = models.BooleanField(default=False)

    # owner = None  # TODO: Add FK to Owner.

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project-detail', args=[str(self.id)])

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
    data = models.TextField()

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
