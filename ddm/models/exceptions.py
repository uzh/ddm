from django.db import models
from ddm.models import DonationProject, Participant


class ExceptionLogEntry(models.Model):
    date = models.DateTimeField()
    project = models.ForeignKey(DonationProject, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, null=True, on_delete=models.SET_NULL)
    exception_type = models.IntegerField()
    message = models.TextField()
