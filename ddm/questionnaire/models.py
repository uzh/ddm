import random

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from polymorphic.models import PolymorphicModel

from ddm.core.utils.user_content.template import render_user_content
from ddm.encryption.models import ModelWithEncryptedData
from ddm.datadonation.models import DataDonation
from ddm.questionnaire.exceptions import QuestionValidationError


class FilterConditionMixin:
    """
    Mixin adding utility functions to models with a generic relationship to
    FilterConditions.
    """
    @staticmethod
    def get_filter_config_id(obj):
        if isinstance(obj, QuestionItem):
            return f'item-{obj.pk}'
        else:
            return f'question-{obj.pk}'

    def get_filter_config(self):
        """
        Creates the filter conditions that can be passed to the vue questionnaire.
        """
        filter_conditions = self.filter_conditions.all().order_by('index')
        filter_configs = []
        for i, condition in enumerate(filter_conditions):
            filter_config = {
                'index': condition.index,
                'combinator': condition.combinator,
                'condition_operator': condition.condition_operator,
                'condition_value': condition.condition_value,
                'target': self.get_filter_config_id(condition.target),
                'source': self.get_filter_config_id(condition.source_object)
            }

            # Reset combinator value to None for item with the lowest index.
            if i == 0:
                filter_config['combinator'] = None
            filter_configs.append(filter_config)
        return filter_configs


class QuestionType(models.TextChoices):
    GENERIC = 'generic', 'Generic Question'
    SINGLE_CHOICE = 'single_choice', 'Single Choice Question'
    MULTI_CHOICE = 'multi_choice', 'Multi Choice Question'
    MATRIX = 'matrix', 'Matrix Question'
    SEMANTIC_DIFF = 'semantic_diff', 'Semantic Differential'
    OPEN = 'open', 'Open Question'
    TRANSITION = 'transition', 'Text Block'


class QuestionBase(FilterConditionMixin, PolymorphicModel):
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

    filter_conditions = GenericRelation(
        'FilterCondition',
        content_type_field='target_content_type',
        object_id_field='target_object_id'
    )

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

    def clean(self):
        """ Validate uniqueness before saving to avoid database IntegrityError. """
        if QuestionBase.objects.filter(variable_name=self.variable_name, project=self.project).exclude(pk=self.pk).exists():
            raise ValidationError({'variable_name': 'A variable with this name already exists in the project.'})

    def save(self, *args, **kwargs):
        """ Call clean() before saving to avoid possible database IntegrityError. """
        self.clean()
        super().save(*args, **kwargs)

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

    def get_varname(self):
        return self.variable_name


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


class OpenQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.OPEN

    class DisplayOptions(models.TextChoices):
        SMALL = 'small', 'Small'
        LARGE = 'large', 'Large'
    display = models.CharField(
        max_length=20,
        blank=False,
        choices=DisplayOptions.choices,
        default=DisplayOptions.SMALL,
        help_text='"Small" displays a one-line textfield, "Large" a multiline '
                  'textfield as input.'
    )

    class InputTypes(models.TextChoices):
        TEXT = 'text', 'Any text'
        NUMBER = 'numbers', 'Numbers only'
        EMAIL = 'email', 'Email address'
    input_type = models.CharField(
        max_length=20,
        blank=False,
        choices=InputTypes.choices,
        default=InputTypes.TEXT,
        verbose_name='Input type',
        help_text='Select the type of input allowed.'
    )

    max_input_length = models.IntegerField(
        verbose_name='Maximum input length',
        help_text=(
            "Participants' input cannot exceed this length. If empty, "
            "no input length restriction is enforced."
        ),
        blank=True,
        null=True,
        default=None
    )

    multi_item_response = models.BooleanField(default=False)

    def create_config(self):
        config = super().create_config()
        config['options']['display'] = self.display
        config['options']['input_type'] = self.input_type
        config['options']['max_input_length'] = self.max_input_length
        config['options']['multi_item_response'] = self.multi_item_response
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

    show_scale_headings = models.BooleanField(default=False)

    def create_config(self):
        config = super().create_config()
        config['options']['show_scale_headings'] = self.show_scale_headings
        return config

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


class QuestionItem(FilterConditionMixin, models.Model):
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

    filter_conditions = GenericRelation(
        'FilterCondition',
        content_type_field='target_content_type',
        object_id_field='target_object_id'
    )

    def get_varname(self):
        return f'{self.question.variable_name}-{self.value}'

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

    input_label = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    heading_label = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    value = models.IntegerField()
    secondary_point = models.BooleanField(default=False)

    def serialize_to_config(self):
        scale_config = model_to_dict(self, exclude=['question'])
        return scale_config


class QuestionnaireResponse(ModelWithEncryptedData):
    # Will only ever be deleted, when the project is deleted.
    project = models.ForeignKey('ddm_projects.DonationProject', on_delete=models.CASCADE)
    participant = models.ForeignKey('ddm_participation.Participant', on_delete=models.CASCADE)
    time_submitted = models.DateTimeField(default=timezone.now)
    data = models.BinaryField()


class FilterCondition(models.Model):
    """
    A model to define filter conditions.
    """
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='filter_target',
        help_text='The target question/question item to which this filter applies.'
    )
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey(
        'target_content_type',
        'target_object_id'
    )

    source_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='filter_source',
        help_text='The question/question item whose answer is evaluated against the filter condition.'
    )
    source_object_id = models.PositiveIntegerField()
    source_object = GenericForeignKey(
        'source_content_type',
        'source_object_id'
    )

    # TODO: Ensure index is unique per target.
    index = models.IntegerField(default=1)

    class ConditionCombinators(models.TextChoices):
        AND = 'AND', 'AND'
        OR = 'OR', 'OR'

    combinator = models.CharField(
        max_length=3,
        choices=ConditionCombinators.choices,
        default=ConditionCombinators.AND,
        help_text=(
            'Defines whether all conditions (AND) or any (OR) must be met.'
            'In the filter condition with the lowest index, this will be '
            'ignored. The conditions following will be evaluated as a chain, '
            'where AND has higher precedence than OR. E.g., Condition1 OR '
            'Condition2 AND Condition3 OR Condition4 will be evaluated as '
            '"Condition1 OR (Condition2 AND Condition3) OR Condition4".'
        )
    )

    # TODO: Which operators are available depends on the source; if the source is of type OpenQuestion, greater/smaller operations should be disallowed.
    class ConditionOperators(models.TextChoices):
        EQUALS = '==', 'Equal (==)'
        EQUALS_NOT = '!=', 'Not Equal (!=)'
        GREATER_THAN = '>', 'Greater than (>)'
        SMALLER_THAN = '<', 'Smaller than (<)'
        GREATER_OR_EQUAL_THAN = '>=', 'Greater than or equal (>=)'
        SMALLER_OR_EQUAL_THAN = '<=', 'Smaller than or equal (<=)'
        CONTAINS = 'contains', 'Contains'
        CONTAINS_NOT = 'contains_not', 'Does not Contain'

    condition_operator = models.CharField(
        max_length=20,
        choices=ConditionOperators.choices,
        default=ConditionOperators.EQUALS,
        help_text='The condition operator for filtering.'
    )

    condition_value = models.JSONField(
        blank=True,
        null=True,
        help_text='The value to compare the source question\'s answer against.'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['target_content_type', 'target_object_id', 'index'],
                name='unique_index_per_target'
            )
        ]

    def save(self, *args, **kwargs):
        # Restrict comparison operators for text-based questions
        if isinstance(self.source_object, OpenQuestion) and self.condition_operator in ['>', '<', '>=', '<=']:
            raise ValueError(f'Operator {self.condition_operator} is not valid for OpenQuestion.')

        super().save(*args, **kwargs)
