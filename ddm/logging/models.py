from django.db import models
from django.utils import timezone


class ExceptionRaisers(models.TextChoices):
    SERVER = 'server'
    CLIENT = 'client'


class ExceptionLogEntry(models.Model):
    date = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey(
        'ddm_projects.DonationProject',
        on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        'ddm_participation.Participant',
        null=True,
        on_delete=models.SET_NULL
    )
    blueprint = models.ForeignKey(
        'ddm_datadonation.DonationBlueprint',
        null=True,
        on_delete=models.CASCADE
    )
    raised_by = models.CharField(
        max_length=20,
        choices=ExceptionRaisers.choices,
        blank=True
    )
    exception_type = models.IntegerField(
        null=True
    )
    message = models.TextField()


class EventLogEntry(models.Model):
    date = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey(
        'ddm_projects.DonationProject',
        on_delete=models.CASCADE
    )
    description = models.TextField()
    message = models.TextField()
