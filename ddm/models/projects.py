from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.utils import timezone

from ddm.models import Encryption


class DonationProject(models.Model):
    name = models.CharField(
        max_length=30,
    )
    slug = models.SlugField(
        verbose_name='External Project Slug',
        unique=True
    )
    intro_text = RichTextField(null=True, blank=True)
    outro_text = RichTextField(null=True, blank=True)

    date_created = models.DateTimeField(default=timezone.now)
    public_key = models.TextField(null=True, default=None)

    # owner = None  # TODO: Add FK to Owner.


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
            secret=settings.SECRET_KEY,
            salt=str(self.time_submitted),
            public_key=self.project.public_key
        ).encrypt(self.data)
        super().save(*args, **kwargs)

    def get_decrypted_data(self):
        decrypted_data = Encryption(
            secret=settings.SECRET_KEY,
            salt=str(self.time_submitted),
            public_key=self.project.public_key
        ).decrypt(self.data)
        return decrypted_data
