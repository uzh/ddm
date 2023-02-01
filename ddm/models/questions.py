import random

from ckeditor.fields import RichTextField

from django.db import models
from django.forms import model_to_dict
from django.template import Context, Template

from polymorphic.models import PolymorphicModel

from ddm.models.core import DataDonation
from ddm.models.logs import ExceptionLogEntry, ExceptionRaisers


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
        'DonationProject',
        on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        'DonationBlueprint',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    DEFAULT_QUESTION_TYPE = QuestionType.GENERIC
    question_type = models.CharField(
        max_length=20,
        blank=False,
        choices=QuestionType.choices,
        default=DEFAULT_QUESTION_TYPE
    )

    name = models.CharField(max_length=255)
    index = models.PositiveIntegerField(default=1, verbose_name='Page')

    variable_name = models.SlugField(
        max_length=50,
        null=False,
        verbose_name='Variable name for storing response',
        help_text='Will be used in the data export to identify responses to this question.'
    )

    text = RichTextField(null=True, blank=True, config_name='ddm_ckeditor')
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

    def is_general(self):
        return True if self.blueprint is None else False

    def get_config(self, participant_id, view):
        config = self.create_config()
        config = self.render_config_content(config, participant_id, view)
        return config

    def create_config(self):
        config = {
            'question': self.pk,
            'type': self.question_type,
            'index': self.index,
            'text': self.text,
            'required': self.required,
            'items': [],
            'scale': [],
            'options': {}
        }
        return config

    def log_exception(self, msg):
        ExceptionLogEntry.objects.create(
            project=self.project,
            blueprint=self.blueprint,
            raised_by=ExceptionRaisers.SERVER,
            message='Questionnaire Response Processing Exception: ' + msg
        )

    def render_config_content(self, config, participant, view):
        if self.is_general():
            context_data = None
        else:
            data_donation = DataDonation.objects.get(
                participant=participant,
                blueprint=self.blueprint
            )
            context_data = data_donation.get_decrypted_data()
        config['text'] = self.render_text(config['text'], context_data, view)
        for index, item in enumerate(config['items']):
            item['label'] = self.render_text(item['label'], context_data, view)
            item['label_alt'] = self.render_text(item['label_alt'], context_data, view)
        return config

    @staticmethod
    def render_text(text, context, view):
        if text is not None:
            text = '{% load ddm_graphs static %}\n' + text
        template = Template(text)
        return template.render(Context({'data': context, 'view': view}))

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
                msg = ('Some responses are missing for '
                       f'{self.DEFAULT_QUESTION_TYPE} with ID '
                       f'{self.id}. Got no response for items '
                       f'{[i for i in item_ids if i not in response.keys()]}.')
                self.log_exception(msg)
            elif len(item_ids) < len(response.keys()):
                msg = (f'Got unexpected response keys for '
                       f'{self.DEFAULT_QUESTION_TYPE} with ID {self.id}.'
                       f'Unexpected keys: {[k for k in response.keys() if k not in item_ids]}.')
                self.log_exception(msg)
            else:
                msg = (f'Response does not match the expected items. Items: '
                       f'{sorted(item_ids)}; Keys: {sorted(response.keys())}.')
                self.log_exception(msg)
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
                msg = (f'Got invalid response "{k}: {val}" for multi '
                       f'choice question with ID {self.id}.')
                self.log_exception(msg)
        return


class SingleChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SINGLE_CHOICE

    def validate_response(self, response):
        valid_values = list(self.questionitem_set.all().values_list('value', flat=True))
        valid_values.append(-99)
        if response not in valid_values:
            msg = (f'Got invalid response "{response}" for single choice '
                   f'question with ID {self.id}.')
            self.log_exception(msg)
        return


class MultiChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MULTI_CHOICE

    def validate_response(self, response):
        super().validate_response(response)
        valid_values = [0, 1, -99]
        for k, val in response.items():
            if val not in valid_values:
                msg = (f'Got invalid response "{k}: {val}" for '
                       f'{self.DEFAULT_QUESTION_TYPE} with ID {self.id}.')
                self.log_exception(msg)
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
        'QuestionBase',
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
        'QuestionBase',
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
