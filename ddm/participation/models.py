from typing import Any

from django.core.validators import MinLengthValidator
from django.db import IntegrityError, models

from ddm.core.utils.misc import create_asciidigits_id
from ddm.datadonation.models import DataDonation


def get_extra_data_default() -> dict[str, dict]:
    """Return default value for Participant.extra_data."""
    return {"url_param": {}}


EXTERNAL_ID_LENGTH = 24  # Length of participant external ID


class Participant(models.Model):
    project = models.ForeignKey(
        "ddm_projects.DonationProject", on_delete=models.CASCADE
    )

    external_id = models.CharField(
        unique=True,
        null=False,
        max_length=EXTERNAL_ID_LENGTH,
        validators=[MinLengthValidator(EXTERNAL_ID_LENGTH)],
    )

    # Participation statistics.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    current_step = models.IntegerField(blank=True, null=True)

    extra_data = models.JSONField(default=get_extra_data_default)

    def __str__(self) -> str:
        return self.external_id

    def save(self, *args, **kwargs) -> None:
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

        return super().save(*args, **kwargs)

    def get_context_data(self) -> dict[str, Any]:
        """
        Returns data that can be accessed when participant is passed to a
        template as a context variable.
        """
        context_data = {
            "participant_id": self.external_id,
            "url_parameter": self.extra_data["url_param"],
            "donation_info": self.get_donation_info(),
        }
        if "briefing_consent" in self.extra_data:
            context_data["briefing_consent"] = self.extra_data["briefing_consent"]
        return context_data

    def get_donation_info(self) -> dict[str, Any]:
        donations = DataDonation.objects.filter(participant=self)
        ExtractionState = DataDonation.DataExtractionState  # noqa: N806
        return {
            "n_success": donations.filter(
                data_extraction_state=ExtractionState.DATA_EXTRACTED
            ).count(),
            "n_pending": donations.filter(
                data_extraction_state=ExtractionState.NO_DATA_EXTRACTED
            ).count(),
            "n_failed": donations.filter(
                data_extraction_state=ExtractionState.FAILED
            ).count(),
            "n_consent": donations.filter(
                data_extraction_state=ExtractionState.DATA_EXTRACTED, consent=True
            ).count(),
            "n_no_consent": donations.filter(
                data_extraction_state=ExtractionState.DATA_EXTRACTED, consent=False
            ).count(),
            "n_no_data_extracted": donations.filter(
                data_extraction_state=ExtractionState.NO_DATA_EXTRACTED
            ).count(),
        }
