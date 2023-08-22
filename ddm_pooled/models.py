from ckeditor_uploader.fields import RichTextUploadingField
from ddm.models.core import create_asciidigits_id
from django.db import models


class PooledProject(models.Model):
    project = models.OneToOneField('ddm.DonationProject', on_delete=models.CASCADE)
    external_id = models.CharField(max_length=50, null=False, unique=True)

    get_donation_consent = models.BooleanField(default=True)
    donation_briefing = RichTextUploadingField(
        null=True, blank=True,
        verbose_name='Donation Briefing Text',
        help_text='If "get donation consent" is enabled, will be displayed before '
                  'the debriefing page.',
        config_name='ddm_ckeditor'
    )


class PoolParticipant(models.Model):
    participant = models.OneToOneField('ddm.Participant', on_delete=models.CASCADE)
    external_id = models.CharField(max_length=24, unique=True)
    pool_id = models.CharField(max_length=24)
    pool_donate = models.BooleanField(default=None, null=True)
    pooled_project = models.ForeignKey('PooledProject', on_delete=models.CASCADE)

    def get_status(self):
        return 'completed' if self.participant.completed else 'started'

    def save(self, *args, **kwargs):
        if self.pk is None:
            new_external_id = create_asciidigits_id()
            while len(PoolParticipant.objects.filter(external_id=new_external_id)) != 0:
                new_external_id = create_asciidigits_id()
            self.external_id = new_external_id
        super().save(*args, **kwargs)
