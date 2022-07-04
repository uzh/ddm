import json

from ckeditor.fields import RichTextField

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from ddm.models import DonationProject, Participant, ModelWithEncryptedData


import logging
logger = logging.getLogger(__name__)

COMMA_SEPARATED_STRINGS_VALIDATOR = RegexValidator(
    r'^((["][^"]+["]))(\s*,\s*((["][^"]+["])))*[,\s]*$',
    message=(
        'Field must contain one or multiple comma separated strings. '
        'Strings must be enclosed in double quotes ("string").'
    )
)


class ZippedBlueprint(models.Model):
    name = models.CharField(max_length=250)
    project = models.ForeignKey(
        DonationProject,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    def get_slug(self):
        return 'zip-blueprint'

    def get_absolute_url(self):
        return reverse('zipped-blueprint-edit', args=[str(self.project_id), str(self.id)])

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

    class FileFormats(models.TextChoices):
        JSON_FORMAT = 'json'
        # CSV_FORMAT = 'csv',
        # HTML_FORMAT = 'html',
        # XLSX_FORMAT = 'xlsx',

    exp_file_format = models.CharField(
        max_length=10,
        choices=FileFormats.choices,
        default=FileFormats.JSON_FORMAT,
        verbose_name='Expected file format',
    )

    expected_fields = models.TextField(
        null=False,
        blank=False,
        validators=[COMMA_SEPARATED_STRINGS_VALIDATOR],
        help_text='Put the field names in double quotes (") and separate them with commas ("Field A", "Field B").'
    )
    extracted_fields = models.TextField(
        null=True,
        blank=True,
        validators=[COMMA_SEPARATED_STRINGS_VALIDATOR],
        help_text='Put the field names in double quotes (") and separate them with commas ("Field A", "Field B").'
    )

    # Configuration if related to ZippedBlueprint:
    zip_blueprint = models.ForeignKey(
        ZippedBlueprint,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Zip container',
    )
    regex_path = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blueprint-edit', args=[str(self.project_id), str(self.id)])

    def get_slug(self):
        return 'blueprint'

    def get_config(self):
        config = {
            'id': self.pk,
            'name': self.name,
            'format': self.exp_file_format,
            'f_expected': json.loads("[" + str(self.expected_fields) + "]"),
            'f_extract': json.loads("[" + str(self.extracted_fields) + "]"),
            'regex_path': self.regex_path,
        }
        return config

    def get_instructions(self):
        return [{'index': i.index, 'text': i.text} for i in self.donationinstruction_set.all()]

    def get_associated_questions(self):
        return self.questionbase_set.all()

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
            consent=data['consent'],
            status=data['status'],
            data=data['extracted_data']
        )
        return


class DataDonation(ModelWithEncryptedData):
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
    time_submitted = models.DateTimeField(default=timezone.now)
    consent = models.BooleanField(default=False)
    status = models.JSONField()
    data = models.BinaryField()


class DonationInstruction(models.Model):
    text = RichTextField(null=True, blank=True)
    index = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
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

    def get_query_object(self):
        if self.blueprint:
            query_object = self.blueprint
        else:
            query_object = self.zip_blueprint
        return query_object

    def clean(self):
        # Ensure that instruction is correctly linked to one blueprint type.
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

        # Ensure that index of instruction page is not greater than set of existing instructions + 1.
        n_instructions = self.get_query_object().donationinstruction_set.count()
        if self.pk:
            if self.index > n_instructions:
                raise ValidationError(
                    f'Index must be in range 1 to {n_instructions}.'
                )
        else:
            if self.index > (n_instructions + 1):
                raise ValidationError(
                    f'Index must be in range 1 to {n_instructions + 1}.'
                )
        super().clean()

    def save(self, *args, **kwargs):
        if kwargs.pop('ignore_index_check', False):
            return super().save()

        # TODO: Optimize and prettify the following part:
        initial_index = DonationInstruction.objects.get(pk=self.pk).index if self.pk else None
        index_taken = self.get_query_object().donationinstruction_set.filter(index=self.index).exclude(pk=self.pk).exists()
        if index_taken and (self.index != initial_index):

            # Account for unique constraint by doing a "proxy"-save to free index.
            target_index = self.index
            self.index = self.get_query_object().donationinstruction_set.count() + 5
            super().save()

            # Change indices of involved objects:
            queryset = self.get_query_object().donationinstruction_set.exclude(pk=self.pk)
            if initial_index is None:
                queryset = queryset.filter(index__gte=target_index).order_by('-index')
                for q in queryset:
                    q.index += 1
                for q in queryset:
                    q.save(ignore_index_check=True)
            elif target_index < initial_index:
                queryset = queryset.filter(index__gte=target_index, index__lt=initial_index).order_by('-index')
                for q in queryset:
                    q.index += 1
                for q in queryset:
                    q.save(ignore_index_check=True)
            elif target_index > initial_index:
                queryset = queryset.filter(index__gt=initial_index, index__lte=target_index).order_by('index')
                for q in queryset:
                    q.index -= 1
                for q in queryset:
                    q.save(ignore_index_check=True)

            # Revert "proxy"-save.
            self.index = target_index
            return super().save()

        return super().save()

    def delete(self, *args, **kwargs):
        """ This model has a post_delete signal processor (see signals.py). """
        super().delete(*args, **kwargs)
