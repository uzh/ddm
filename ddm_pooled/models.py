from django.db import models


class PooledProject(models.Model):
    project = models.OneToOneField('ddm.DonationProject', on_delete=models.CASCADE)


# class PoolParticipant(models.Model):
#     participant = models.ForeignKey('ddm.Participant', on_delete=models.CASCADE)
#     pool_part = models.CharField(max_length=24)
#    pool_donate = models.BooleanField(default=False)

