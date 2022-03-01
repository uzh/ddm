from django.db import models
from ckeditor.fields import RichTextField


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

    time_submitted = models.DateTimeField()
    data = models.JSONField()
