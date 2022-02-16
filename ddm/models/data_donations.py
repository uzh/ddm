from django.db import models
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)


class ZippedBlueprint(models.Model):
    name = models.CharField(
        max_length=250
    )
    project = None

    def get_blueprints(self):
        blueprints = DonationBlueprint.objects.filter(zip_blueprint=self)
        return blueprints

    def get_config(self):
        config = {
            'ul_type': 'zip',
            'blueprints': []
        }
        blueprints = self.get_blueprints()
        for bp in blueprints:
            config['blueprints'].append(bp.get_config())
        return config


# TODO: Add validation on save to ensure that regex_path != None when zip_blueprint != None
class DonationBlueprint(models.Model):
    name = models.CharField(
        max_length=250
    )
    project = None  # Relation to DonationProject
    instructions = None

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

    def get_config(self):
        config = {
            'id': self.pk,
            'format': self.exp_file_format,
            'f_expected': self.expected_fields,
            'f_extract': self.extracted_fields,
            'regex_path': self.regex_path
        }
        return config

    def process_donation(self, data):
        if self.validate_donation(data):
            self.create_donation(data)
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

    def create_donation(self, data):
        DataDonation.objects.create(
            blueprint=self,
            time=timezone.now().isoformat(),
            consent=data['consent'],
            status=data['status'],
            data=data['extracted_data']
        )
        return


class DataDonation(models.Model):
    project = None  # FK to project
    blueprint = models.ForeignKey(
        DonationBlueprint,
        null=True,
        on_delete=models.SET_NULL
    )
    id = None  # Uploader ID
    time = models.DateTimeField()
    consent = models.BooleanField(default=False)
    status = models.JSONField()
    data = models.JSONField()
