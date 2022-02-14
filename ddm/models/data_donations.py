from django.db import models


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
            self.save_donation(data)
        else:
            # TODO: Handle  problem
            pass
        return

    def validate_donation(self, data):
        pass

    def save_donation(self, data):
        pass


class DataDonation(models.Model):
    blueprint = None  # FK to Donation Blueprint
    id = None  # Uploader ID
    data = models.JSONField()
