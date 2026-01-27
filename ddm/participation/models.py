from django.core.validators import MinLengthValidator
from django.db import models, IntegrityError

from ddm.auth.models import ProjectAccessToken
from ddm.core.utils.misc import create_asciidigits_id
from ddm.datadonation.models import DataDonation
from ddm.logging.models import ExceptionLogEntry, EventLogEntry


def get_extra_data_default():
    """ Return default value for Participant.extra_data. """
    return dict(url_param=dict())

EXTERNAL_ID_LENGTH = 24  # Length of participant external ID

class Participant(models.Model):
    project = models.ForeignKey('ddm_projects.DonationProject', on_delete=models.CASCADE)

    external_id = models.CharField(
        unique=True, null=False,
        max_length=EXTERNAL_ID_LENGTH,
        validators=[MinLengthValidator(EXTERNAL_ID_LENGTH)]
    )

    # Participation statistics.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    current_step = models.IntegerField(blank=True, null=True)

    extra_data = models.JSONField(default=get_extra_data_default)

    def __str__(self):
        return self.external_id

    def get_context_data(self):
        """
        Returns data that can be accessed when participant is passed to a
        template as a context variable.
        """
        context_data = {
            'participant_id': self.external_id,
            'url_parameter': self.extra_data['url_param'],
            'donation_info': self.get_donation_info(),
        }
        if 'briefing_consent' in self.extra_data:
            context_data['briefing_consent'] = self.extra_data['briefing_consent']
        return context_data

    def get_donation_info(self):
        donations = DataDonation.objects.filter(participant=self)
        donation_info = {
            'n_success': donations.filter(status='success').count(),
            'n_pending': donations.filter(status='pending').count(),
            'n_failed': donations.filter(status='failed').count(),
            'n_consent': donations.filter(status='success', consent=True).count(),
            'n_no_consent': donations.filter(status='success', consent=False).count(),
            'n_no_data_extracted': donations.filter(status='nothing extracted').count()
        }
        return donation_info

    def save(self, *args, **kwargs):
        if self.pk is None:

            max_attempts = 5
            for attempt in range(max_attempts):
                self.external_id = create_asciidigits_id(EXTERNAL_ID_LENGTH)
                try:
                    return super().save(*args, **kwargs)
                except IntegrityError:
                    if attempt == max_attempts - 1:
                        raise
                    continue

        super().save(*args, **kwargs)
