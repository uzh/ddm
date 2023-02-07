from django.db import models
from django.utils import timezone


class ExceptionRaisers(models.TextChoices):
    SERVER = 'server'
    CLIENT = 'client'


class ExceptionLogEntry(models.Model):
    date = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey(
        'DonationProject',
        on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        'Participant',
        null=True,
        on_delete=models.SET_NULL
    )
    blueprint = models.ForeignKey(
        'DonationBlueprint',
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
        'DonationProject',
        on_delete=models.CASCADE
    )
    description = models.CharField(max_length=100)
    message = models.TextField()
