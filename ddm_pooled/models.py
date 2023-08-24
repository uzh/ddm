from ckeditor_uploader.fields import RichTextUploadingField
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
