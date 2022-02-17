from django.db import models


class DonationProject(models.Model):
    name = models.CharField(
        max_length=30,
    )
    slug = models.SlugField(
        verbose_name='External Project Slug',
        unique=True
    )
    # owner = None  # FK to User


class Participant(models.Model):
    project = models.ForeignKey(
        DonationProject,
        on_delete=models.CASCADE
    )

    # Participation statistics.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
