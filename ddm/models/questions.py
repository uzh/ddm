import random

from ckeditor.fields import RichTextField
from django.db import models
from django.forms import model_to_dict
from django.template import Context, Template

from polymorphic.models import PolymorphicModel
from ddm.models import DonationProject, DonationBlueprint, DataDonation

import logging
logger = logging.getLogger(__name__)


class QuestionType(models.TextChoices):
    GENERIC = 'generic', 'Generic Question'
    SINGLE_CHOICE = 'single_choice', 'Single Choice Question'
    MULTI_CHOICE = 'multi_choice', 'Multi Choice Question'
    MATRIX = 'matrix', 'Matrix Question'
    SEMANTIC_DIFF = 'semantic_diff', 'Semantic Differential'
    OPEN = 'open', 'Open Question'
    TRANSITION = 'transition', 'Transition Block'


class QuestionBase(PolymorphicModel):
    project = models.ForeignKey(
        DonationProject,
        on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        DonationBlueprint,
        on_delete=models.CASCADE
    )

    DEFAULT_QUESTION_TYPE = QuestionType.GENERIC
    question_type = models.CharField(
        max_length=20,
        blank=False,
        choices=QuestionType.choices,
        default=DEFAULT_QUESTION_TYPE
    )

    name = models.CharField(max_length=255)
    index = models.PositiveIntegerField(default=1)

    variable_name = models.SlugField(
        max_length=50,
        null=False
    )

    text = RichTextField(null=True, blank=True)
    required = models.BooleanField(default=False)

    class Meta:
        ordering = ['index']
        constraints = [
            models.UniqueConstraint(
                fields=['variable_name', 'project'],
                name='unique_varname_per_project'
            ),
        ]

    def __init__(self, *args, **kwargs):
        kwargs['question_type'] = self.DEFAULT_QUESTION_TYPE
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_config(self, participant_id):
        config = self.create_config()
        config = self.render_config_content(config, participant_id)
        return config

    def create_config(self):
        config = {
            'question': self.pk,
            'type': self.question_type,
            'index': self.index,
            'text': self.text,
            'items': [],
            'scale': [],
            'options': {}
        }
        return config

    def render_config_content(self, config, participant):
        data_donation = DataDonation.objects.get(
            participant=participant,
            blueprint=self.blueprint
        )
        context_data = data_donation.data
        config['text'] = self.render_text(config['text'], context_data)
        for index, item in enumerate(config['items']):
            item['label'] = self.render_text(item['label'], context_data)
            item['label_alt'] = self.render_text(item['label_alt'], context_data)
        return config

    @staticmethod
    def render_text(text, context):
        template = Template(text)
        return template.render(Context({'data': context}))

    def validate_response(self, response):
        return


class ItemMixin(models.Model):
    randomize_items = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def create_config(self):
        config = super().create_config()
        config = self.add_item_config(config)
        return config

    def add_item_config(self, config):
        items = QuestionItem.objects.filter(question=self)
        for item in items:
            config['items'].append(item.serialize_to_config())

        if self.randomize_items:
            random.shuffle(config['items'])
        return config

    def validate_response(self, response):
        # Validate that all items have a response.
        item_ids = [str(i) for i in list(self.questionitem_set.all().values_list('id', flat=True))]
        if not sorted(item_ids) == sorted(response.keys()):
            if len(item_ids) > len(response.keys()):
                logger.error(
                    f'Some responses are missing for {self.DEFAULT_QUESTION_TYPE} with ID {self.id}.'
                    f'Got no response for items {[i for i in item_ids if i not in response.keys()]}.'
                )
            elif len(item_ids) < len(response.keys()):
                logger.error(
                    f'Got unexpected response keys for {self.DEFAULT_QUESTION_TYPE} with ID {self.id}.'
                    f'Unexpected keys: {[k for k in response.keys() if k not in item_ids]}.'
                )
            else:
                logger.error(
                    f'Response does not match the expected items. '
                    f'Items: {sorted(item_ids)}; Keys: {sorted(response.keys())}.'
                )
        return


class ScaleMixin:
    def create_config(self):
        config = super().create_config()
        config = self.add_scale_config(config)
        return config

    def add_scale_config(self, config):
        scale_points = ScalePoint.objects.filter(question=self)
        for point in scale_points:
            config['scale'].append(point.serialize_to_config())
        return config

    def validate_response(self, response):
        super().validate_response(response)
        valid_values = list(self.scalepoint_set.all().values_list('value', flat=True))
        valid_values.append(-99)
        for k, val in response.items():
            if val not in valid_values:
                logger.error(f'Got invalid response "{k}: {val}" for multi '
                             f'choice question with ID {self.id}.')
        return


class SingleChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SINGLE_CHOICE

    def validate_response(self, response):
        valid_values = list(self.questionitem_set.all().values_list('value', flat=True))
        valid_values.append(-99)
        if response not in valid_values:
            logger.error(f'Got invalid response "{response}" for single choice '
                         f'question with ID {self.id}.')
        return


class MultiChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MULTI_CHOICE

    def validate_response(self, response):
        super().validate_response(response)
        valid_values = [0, 1, -99]
        for k, val in response.items():
            if val not in valid_values:
                logger.error(f'Got invalid response "{k}: {val}" for '
                             f'{self.DEFAULT_QUESTION_TYPE} with ID {self.id}.')
        return


class OpenQuestion(QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.OPEN

    class DisplayOptions(models.TextChoices):
        SMALL = 'small', 'Small'
        LARGE = 'large', 'Large'
    display = models.CharField(
        max_length=20,
        blank=False,
        choices=DisplayOptions.choices,
        default=DisplayOptions.LARGE
    )

    def create_config(self):
        config = super().create_config()
        config['options']['display'] = self.display
        return config

    def validate_response(self, response):
        # TODO: Think about if it's necessary to add some validation steps here.
        return


class MatrixQuestion(ScaleMixin, ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MATRIX


class SemanticDifferential(ScaleMixin, ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SEMANTIC_DIFF


class Transition(QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.TRANSITION


class QuestionItem(models.Model):
    class Meta:
        ordering = ['index']

    question = models.ForeignKey(
        QuestionBase,
        on_delete=models.CASCADE
    )
    label = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    label_alt = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    index = models.IntegerField()
    value = models.IntegerField()
    randomize = models.BooleanField(default=False)

    def serialize_to_config(self):
        item_config = model_to_dict(self, exclude=['question'])
        return item_config


class ScalePoint(models.Model):
    class Meta:
        ordering = ['index']
        constraints = [
            models.UniqueConstraint(
                fields=['index', 'question'],
                name='unique_index_per_question'
            ),
        ]

    question = models.ForeignKey(
        QuestionBase,
        on_delete=models.CASCADE
    )
    index = models.IntegerField()
    label = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    value = models.IntegerField()
    add_border = models.BooleanField(default=False)

    def serialize_to_config(self):
        scale_config = model_to_dict(self, exclude=['question', 'add_border'])
        return scale_config
