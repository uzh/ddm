from django.db import models

from ddm.models import DonationBlueprint


class DonationProject(models.Model):
    name = models.CharField(
        max_length=30,
    )
    slug = models.SlugField(
        verbose_name='External Project Slug',
        unique=True
    )
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
    blueprint = models.ForeignKey(
        DonationBlueprint,
        on_delete=models.SET_NULL,
        null=True
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE
    )

    time_submitted = models.DateTimeField()
    responses = models.JSONField
