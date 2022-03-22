from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ddm.models import DonationProject, Participant

import logging
logger = logging.getLogger(__name__)


class ZippedBlueprint(models.Model):
    name = models.CharField(max_length=250)
    project = models.ForeignKey(
        DonationProject,
        on_delete=models.CASCADE
    )

    def get_blueprints(self):
        blueprints = DonationBlueprint.objects.filter(zip_blueprint=self)
        return blueprints

    def get_configs(self):
        bp_configs = []
        blueprints = self.get_blueprints()
        for bp in blueprints:
            bp_configs.append(bp.get_config())
        return bp_configs

    def get_instructions(self):
        return [{'index': i.index, 'text': i.text} for i in self.donationinstruction_set.all()]


# TODO: For admin section: Add validation on save to ensure that regex_path != None when zip_blueprint != None
class DonationBlueprint(models.Model):
    project = models.ForeignKey(
        DonationProject,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=250)
    instructions = None

    class FileFormats(models.TextChoices):
        JSON_FORMAT = 'json'
        # CSV_FORMAT = 'csv',
        # HTML_FORMAT = 'html',
        # XLSX_FORMAT = 'xlsx',

    exp_file_format = models.CharField(
        max_length=10,
        choices=FileFormats.choices,
        default=FileFormats.JSON_FORMAT,
    )

    expected_fields = models.JSONField()
    extracted_fields = models.JSONField()

    # Configuration if related to ZippedBlueprint:
    zip_blueprint = models.ForeignKey(
        ZippedBlueprint,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    regex_path = models.TextField(
        null=True,
        blank=True
    )

    def get_config(self):
        config = {
            'id': self.pk,
            'name': self.name,
            'format': self.exp_file_format,
            'f_expected': self.expected_fields,
            'f_extract': self.extracted_fields,
            'regex_path': self.regex_path,
        }
        return config

    def get_instructions(self):
        return [{'index': i.index, 'text': i.text} for i in self.donationinstruction_set.all()]

    def process_donation(self, data, participant):
        if self.validate_donation(data):
            self.create_donation(data, participant)
        else:
            logger.error(f'Donation not processed by blueprint {self.pk}')
        return

    @staticmethod
    def validate_donation(data):
        # Check if all expected fields are in response.
        response_fields = ['consent', 'extracted_data', 'status']
        if not all(k in data for k in response_fields):
            logger.error(
                'Donation data does not contain the expected information. '
                f'Expected key: {response_fields}; '
                f'Present fields: {data.keys()}.'
            )
            return False

        # TODO: Add other validation steps? - e.g., validation of extracted fields
        return True

    def create_donation(self, data, participant):
        DataDonation.objects.create(
            project=self.project,
            blueprint=self,
            participant=participant,
            time=timezone.now().isoformat(),
            consent=data['consent'],
            status=data['status'],
            data=data['extracted_data']
        )
        return


class DataDonation(models.Model):
    project = models.ForeignKey(
        DonationProject,
        on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        DonationBlueprint,
        null=True,
        on_delete=models.SET_NULL
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE
    )
    time = models.DateTimeField()
    consent = models.BooleanField(default=False)
    status = models.JSONField()
    data = models.JSONField()


class DonationInstruction(models.Model):
    text = RichTextField(null=True, blank=True)
    index = models.PositiveIntegerField(default=1)
    blueprint = models.ForeignKey(
        DonationBlueprint,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    zip_blueprint = models.ForeignKey(
        ZippedBlueprint,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['index']
        constraints = [
            models.UniqueConstraint(
                fields=['index', 'blueprint'],
                name='unique_index_per_blueprint'
            ),
            models.UniqueConstraint(
                fields=['index', 'zip_blueprint'],
                name='unique_index_per_zipblueprint'
            ),
        ]

    def clean(self):
        if not self.blueprint and not self.zip_blueprint:
            raise ValidationError(
                'Must be linked to either a DonationBlueprint or '
                'a ZippedBlueprint.'
            )
        if self.blueprint and self.zip_blueprint:
            raise ValidationError(
                'Must be linked to either a DonationBlueprint or '
                'a ZippedBlueprint, but not both.'
            )
        super().clean()
