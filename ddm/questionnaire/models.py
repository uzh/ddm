import random

from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from polymorphic.models import PolymorphicModel

from ddm.core.utils.user_content.template import render_user_content
from ddm.encryption.models import ModelWithEncryptedData
from ddm.datadonation.models import DataDonation
from ddm.questionnaire.exceptions import QuestionValidationError


class QuestionType(models.TextChoices):
    GENERIC = 'generic', 'Generic Question'
    SINGLE_CHOICE = 'single_choice', 'Single Choice Question'
    MULTI_CHOICE = 'multi_choice', 'Multi Choice Question'
    MATRIX = 'matrix', 'Matrix Question'
    SEMANTIC_DIFF = 'semantic_diff', 'Semantic Differential'
    OPEN = 'open', 'Open Question'
    TRANSITION = 'transition', 'Text Block'


class QuestionBase(PolymorphicModel):
    project = models.ForeignKey(
        'ddm_projects.DonationProject',
        on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        'ddm_datadonation.DonationBlueprint',
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
    page = models.PositiveIntegerField(default=1, verbose_name='Page')
    index = models.PositiveIntegerField(default=1, verbose_name='Index')

    variable_name = models.SlugField(
        max_length=50,
        null=False,
        verbose_name='Variable name for storing response',
        help_text='Will be used in the data export to identify responses to this question.'
    )

    text = models.TextField(
        blank=True,
        help_text=(
            'If a question is linked to a File Blueprint, data points from the donated data associated with the linked donation blueprint can be included in the question text. '
            'This data can be included as "{{ data }}" in the question text. '
            'It is possible to subset the data object (e.g., to include the last datapoint you can use {{ data.0 }} or include advanced '
            'rendering options included in the Django templating engine. For a more comprehensive overview and examples see the documentation. '
            'Additionally, information directly related to the participant can be included in the question text. '
            'This information can be referenced as "{{ participant }}".'
        )
    )
    required = models.BooleanField(default=False)

    class Meta:
        ordering = ['page', 'index']
        constraints = [
            models.UniqueConstraint(
                fields=['variable_name', 'project'],
                name='unique_varname_per_project'
            ),
        ]

    def __init__(self, *args, **kwargs):
        if not args:
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
            'page': self.page,
            'index': self.index,
            'text': self.text,
            'required': self.required,
            'items': [],
            'scale': [],
            'options': {}
        }
        return config

    def render_config_content(self, config, participant, view):
        """
        Renders references to donated data or participant data in question or
        item text configurations as html.
        """
        if self.is_general():
            donated_data = None
        else:
            data_donation = DataDonation.objects.get(
                participant=participant,
                blueprint=self.blueprint
            )
            donated_data = data_donation.get_decrypted_data(
                secret=self.project.secret_key, salt=self.project.get_salt())

        context = {}
        context.update(participant.get_context_data())
        context.update({'donated_data': donated_data})

        config['text'] = render_user_content(config['text'], context)
        for index, item in enumerate(config['items']):
            item['label'] = render_user_content(item['label'], context)
            item['label_alt'] = render_user_content(item['label_alt'], context)
        return config


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

    def validate_item_response(self, response):
        """
        Checks if all expected item ids are present in response.
        Expects the response to be a dictionary of the form:
        {'item id as string': <item response>, ...}

        Raises a KeyError if validation fails.
        """
        question_items = self.questionitem_set.all().values_list('id', flat=True)
        item_ids = [str(i) for i in list(question_items)]
        response_keys = [str(k) for k in response.keys()]
        if sorted(item_ids) == sorted(response_keys):
            return True

        if len(item_ids) > len(response_keys):
            missing_items = [i for i in item_ids if i not in response_keys]
            raise KeyError(f'Missing expected items: {missing_items}.')
        elif len(item_ids) < len(response_keys):
            unexpected_items = [k for k in response_keys if k not in item_ids]
            raise KeyError(
                f'Unexpected item ids for {self.DEFAULT_QUESTION_TYPE} '
                f'with ID {self.id}: {unexpected_items}.')
        else:
            raise KeyError(
                f'Received response items ({sorted(response_keys)}) do '
                f'not match the expected items ({sorted(item_ids)}).')


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

    def validate_scale_response(self, response):
        """
        Checks if all responses are possible values according to the scale
        definition.
        {'item id as string': <item response>, ...}

        Raises a KeyError if validation fails.
        """
        scale_points = self.scalepoint_set.all()
        valid_values = list(scale_points.values_list('value', flat=True))
        valid_values.append(-99)

        errors = []
        for item, value in response.items():
            if isinstance(value, float):
                raise QuestionValidationError(
                    question=self,
                    message=f'Response {value} is of type float.')

            try:
                value = int(value)
            except (ValueError, TypeError):
                errors.append(f'Response {value} for item {item} '
                              f'cannot be converted to int.')
                continue

            if int(value) not in valid_values:
                errors.append(f'Got invalid response "{item}: {value}"')

        return errors


class SingleChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SINGLE_CHOICE

    def get_valid_values(self):
        """
        Valid response values include all related item values
        (QuestionItem.value) plus -99 which indicates that a question was not
        answered/skipped.
        """
        question_items = self.questionitem_set.all()
        valid_values = list(question_items.values_list('value', flat=True))
        valid_values.append(-99)
        return valid_values

    def validate_response(self, response):
        """
        Expects the response to be a single value as either an integer or a
        string that can be converted to an integer.
        """
        valid_values = self.get_valid_values()

        if isinstance(response, float):
            raise QuestionValidationError(
                question=self,
                message=f'{response} is of type float.')

        try:
            response = int(response)
        except (ValueError, TypeError):
            raise QuestionValidationError(
                question=self,
                message=f'{response} cannot be converted to int.')

        if response not in valid_values:
            raise QuestionValidationError(
                question=self,
                message=f'{response} invalid; valid values: {valid_values}.')
        return True


class MultiChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MULTI_CHOICE

    def get_valid_values(self):
        """
        Valid response values include 0 (item not selected), 1 (item selected),
        and -99 which indicates that a question was not answered/skipped.
        """
        valid_values = [0, 1, -99]
        return valid_values

    def validate_response(self, response):
        """
        Expects the response to be a dictionary of the form:
        {'item id as string': <1/0/-99>, ...}
        """
        errors = []
        try:
            self.validate_item_response(response)
        except KeyError as e:
            errors.append(e)

        valid_values = self.get_valid_values()
        for item, value in response.items():
            if isinstance(value, float):
                errors.append(f'Got invalid response {value} for item {item}.')
                continue

            try:
                value = int(value)
            except (ValueError, TypeError):
                errors.append(f'Response {response} for item {item} '
                              f'cannot be converted to int.')
                continue

            if value not in valid_values:
                errors.append(f'Got invalid response {value} for item {item}.')

        if errors:
            raise QuestionValidationError(question=self, item_errors=errors)
        return True


class OpenQuestion(QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.OPEN

    class DisplayOptions(models.TextChoices):
        SMALL = 'small', 'Small'
        LARGE = 'large', 'Large'
    display = models.CharField(
        max_length=20,
        blank=False,
        choices=DisplayOptions.choices,
        default=DisplayOptions.LARGE,
        help_text='"Small" displays a one-line textfield, "Large" a multiline '
                  'textfield as input.'
    )

    def create_config(self):
        config = super().create_config()
        config['options']['display'] = self.display
        return config

    def validate_response(self, response):
        """ Any value representable as a String is a valid response. """
        try:
            str(response)
        except TypeError:
            raise QuestionValidationError(question=self)
        return True


class MatrixQuestion(ScaleMixin, ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MATRIX

    def validate_response(self, response):
        """
        Expects the response to be a dictionary of the form:
        {'item id as string': <1/0/-99>, ...}
        """
        item_errors = []
        try:
            self.validate_item_response(response)
        except KeyError as e:
            item_errors.append(e)

        scale_errors = self.validate_scale_response(response)

        if scale_errors or item_errors:
            raise QuestionValidationError(
                question=self, scale_errors=scale_errors, item_errors=item_errors)
        return True


class SemanticDifferential(ScaleMixin, ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SEMANTIC_DIFF

    def validate_response(self, response):
        """
        Expects the response to be a dictionary of the form:
        {'item id as string': <1/0/-99>, ...}
        """
        item_errors = []
        try:
            self.validate_item_response(response)
        except KeyError as e:
            item_errors.append(e)

        scale_errors = self.validate_scale_response(response)

        if scale_errors or item_errors:
            raise QuestionValidationError(
                question=self, scale_errors=scale_errors, item_errors=item_errors)
        return True


class Transition(QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.TRANSITION

    def validate_response(self, response):
        """
        No validation necessary, as this is just a placeholder question type.
        """
        return True


class QuestionItem(models.Model):
    class Meta:
        ordering = ['index']
        constraints = [
            models.UniqueConstraint(
                fields=['index', 'question'],
                name='unique_item_index_per_question'
            ),
            models.UniqueConstraint(
                fields=['value', 'question'],
                name='unique_item_value_per_question'
            ),
        ]

    question = models.ForeignKey(
        'QuestionBase',
        on_delete=models.CASCADE
    )
    index = models.IntegerField()
    label = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    label_alt = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Label Right"
    )
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
        scale_config = model_to_dict(self, exclude=['question'])
        return scale_config


class QuestionnaireResponse(ModelWithEncryptedData):
    # Will only ever be deleted, when the project is deleted.
    project = models.ForeignKey('ddm_projects.DonationProject', on_delete=models.CASCADE)
    participant = models.ForeignKey('ddm_participation.Participant', on_delete=models.CASCADE)
    time_submitted = models.DateTimeField(default=timezone.now)
    data = models.BinaryField()
