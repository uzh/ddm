from django.db import models


class ExceptionRaisers(models.TextChoices):
    SERVER = 'server'
    CLIENT = 'client'


class ExceptionLogEntry(models.Model):
    date = models.DateTimeField()
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
