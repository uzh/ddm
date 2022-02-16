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
