from django.contrib.postgres.fields import JSONField
from django.db import models


class UploadedData(models.Model):
    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.CASCADE
    )
    upload_id = models.CharField(max_length=10)
    data = JSONField(
        null=True,
        blank=True
    )
    upload_time = models.DateTimeField()


class UploadedDataTemp(models.Model):
    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.CASCADE
    )
    upload_id = models.CharField(max_length=10)
    time = models.DateTimeField()
