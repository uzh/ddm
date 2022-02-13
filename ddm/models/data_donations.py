from django.db import models


class DonationBlueprint(models.Model):
    project = None  # Relation to DonationProject
    instructions = None

    # TODO: Account for different upload modes (i.e., single file and zip) - maybe a separate model?

    class FileFormats(models.TextChoices):
        JSON_FORMAT = 'json'
        # CSV_FORMAT = 'csv',
        # HTML_FORMAT = 'html',
        # XLSX_FORMAT = 'xlsx',

    exp_file_format = models.CharField(
        max_length=10,
        choices=FileFormats.choices,
        default=FileFormats.JSON_TYPE,
    )

    exp_fields = models.JSONField()
    extracted_fields = models.JSONField()

    def get_config(self):
        config = {
            'id': self.pk,
            'format': self.exp_file_format,
            'exp_fields': self.exp_fields,
            'extr_fields': self.extracted_fields
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
