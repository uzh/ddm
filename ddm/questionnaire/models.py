import random
from datetime import datetime
from typing import Union

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from polymorphic.models import PolymorphicModel

from ddm.core.utils.user_content.template import render_user_content
from ddm.encryption.models import ModelWithEncryptedData
from ddm.datadonation.models import DataDonation
from ddm.projects.service import get_participant_variables, get_url_parameters


class FilterConditionMixin:
    """
    Mixin adding utility functions to models with a generic relationship to
    FilterConditions.
    """
    def get_filter_config(self):
        """
        Creates the filter configuration that can be passed to the vue
        questionnaire.

        The filter configuration consists of a list of dictionaries, where each
        dictionary represents the configuration of one filter rule.
        A filter rule configuration has the following keys:

        - 'index': The index (or order) of the condition.
        - 'combinator': The filter combinator (is set to None for the first
            filter condition).
        - 'condition_operator': The operator set for the filter condition.
        - 'condition_value': The value against which the condition is evaluated.
        - 'target': The config ID of the filter target (i.e., the element that
            will be shown/hidden; e.g., 'item-1').
        - 'source': The config ID of the filter source (i.e., the element of
            which the value is compared against the filter condition; e.g., 'item-2').

        Returns:
            list: A list of dictionaries, each holding a filter configuration.
        """
        filter_conditions = self.get_active_filters()
        active_filters = [f for f in filter_conditions if f.check_source_exists()]
        filter_configs = []
        for i, condition in enumerate(active_filters):
            filter_config = {
                'index': condition.index,
                'combinator': condition.combinator,
                'condition_operator': condition.condition_operator,
                'condition_value': condition.condition_value,
                'target': condition.get_target_config_id(),
                'source': condition.get_source_config_id()
            }

            # Reset combinator value to None for item with the lowest index.
            if i == 0:
                filter_config['combinator'] = None
            filter_configs.append(filter_config)
        return filter_configs

    def get_active_filters(self):
        """
        Returns the set of associated filters that are still active.

        Returns:
            queryset
        """
        return self.filtercondition_set.filter(source_exists=True).order_by('index')


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

    def get_config(self, participant_id):
        config = self.create_config()
        config = self.render_config_content(config, participant_id)
        return config

    def get_response_keys(self):
        return []

    def create_config(self):
        config = {
            'question': f'question-{self.pk}',
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

    def render_config_content(self, config, participant):
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

    def get_valid_responses(self):
        """Returns a list of valid responses for this question."""
        default_missing = -99
        return [default_missing]

    def validate_response(self, response_key, response):
        """Placeholder method - must be defined in derivative models."""
        return True


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

    def get_response_keys(self):
        item_pks = self.questionitem_set.all().values_list('pk', flat=True)
        return [f'item-{pk}' for pk in list(item_pks)]


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

    def get_valid_responses(self):
        valid_responses = super().get_valid_responses()
        valid_responses += list(self.scalepoint_set.all().values_list('value', flat=True))
        return valid_responses


class SingleChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SINGLE_CHOICE

    def get_response_keys(self):
        return [f'question-{self.pk}']

    def get_valid_responses(self):
        """
        Valid response values include all related item values
        (QuestionItem.value) plus -99 which indicates that a question was not
        answered/skipped.
        """
        valid_responses = super().get_valid_responses()
        item_values = self.questionitem_set.all().values_list('value', flat=True)
        valid_responses += list(item_values)
        return valid_responses


class MultiChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MULTI_CHOICE

    def get_valid_responses(self):
        """
        Valid response values include 0 (item not selected), 1 (item selected),
        and -99 which indicates that a question was not answered/skipped.
        """
        valid_responses = super().get_valid_responses()
        valid_responses += [0, 1]
        return valid_responses


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

    def get_response_keys(self):
        if self.multi_item_response:
            item_pks = self.questionitem_set.all().values_list('pk', flat=True)
            return [f'item-{pk}' for pk in list(item_pks)]
        else:
            return [f'question-{self.pk}']

    def create_config(self):
        config = super().create_config()
        config['options']['display'] = self.display
        config['options']['input_type'] = self.input_type
        config['options']['max_input_length'] = self.max_input_length
        config['options']['multi_item_response'] = self.multi_item_response

        # Ensure that "left-over" items are not included in config.
        if not self.multi_item_response:
            config['items'] = []
        return config

    def get_valid_responses(self):
        valid_responses = super().get_valid_responses()
        valid_responses += ['__any_string__']
        return valid_responses


class MatrixQuestion(ScaleMixin, ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MATRIX

    show_scale_headings = models.BooleanField(default=False)

    def create_config(self):
        config = super().create_config()
        config['options']['show_scale_headings'] = self.show_scale_headings
        return config

    def get_valid_responses(self):
        valid_responses = super().get_valid_responses()
        return valid_responses


class SemanticDifferential(ScaleMixin, ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SEMANTIC_DIFF

    def get_valid_responses(self):
        valid_responses = super().get_valid_responses()
        return valid_responses


class Transition(QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.TRANSITION


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

    @property
    def variable_name(self):
        return f'{self.question.variable_name}-{self.value}'

    def serialize_to_config(self):
        item_config = model_to_dict(self, exclude=['question'])
        item_config['id'] = f'item-{item_config["id"]}'
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
    data = models.BinaryField()  # Holds the actual response data (encrypted)
    questionnaire_config = models.JSONField(default=list, null=True)  # Holds the questionnaire configuration at the time of participation.


class FilterSourceTypes(models.TextChoices):
    QUESTION = 'question', 'Question'
    QUESTION_ITEM = 'item', 'Question Item'
    URL_PARAMETER = 'url_parameter', 'URL Parameter'
    SYSTEM = 'system', 'System Variable'
    PARTICIPANT = 'participant', 'Participant Variable'
    DONATION = 'donation', 'Donation Information'


class FilterCondition(models.Model):
    """
    A model to define filter conditions that control the visibility of questions
    or question items.

    The filter target (i.e., the entity that should be hidden/displayed) can
    either be a Question or a QuestionItem. This relationship is modelled with
    a foreign key field ensuring for type safety and referential integrity.

    The filter source (i.e., the variable whose value is evaluated in the
    filter condition) can be:
    - A Question or QuestionItem (identifier = primary key)
    - Variables like URL parameters or participation data
      (identifier = variable name, e.g., '_start_time')

    The filter source relationship is modelled using a hybrid approach.
    The source_type field specifies to which type of source the filter condition
    is related (see FilterSourceTypes for implemented source types).
    For Question and QuestionItem sources, the class implements foreign key
    relations (source_question, source_item).
    For variables that are not linked to a database entity, the
    source_identifier attribute holds the information which variable the
    filter condition is linked to. For others, it holds the linked question's
    or item's primary key.

    Note:
        Implicitly linked sources (i.e., variables) are not deleted when the
        source is deleted (e.g., when an url parameter is changed). Instead,
        in these instances source_exists is set to False and index is set to
        -1 * unix timestamp.
    """
    target_question = models.ForeignKey(
        'QuestionBase',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target_item = models.ForeignKey(
        'QuestionItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Source configuration
    source_question = models.ForeignKey(
        'QuestionBase',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dependent_filters'
    )
    source_item = models.ForeignKey(
        'QuestionItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dependent_filters'
    )

    source_type = models.CharField(
        max_length=60,
        choices=FilterSourceTypes.choices,
    )
    source_identifier = models.CharField(max_length=255, null=True, blank=True)

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
        help_text='The value to compare the source\'s value against.'
    )

    source_exists = models.BooleanField(default=True)  # Is set to false if non-fk source does not exist anymore.

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['target_item', 'target_question', 'index'],
                name='unique_index_per_target'
            )
        ]

    def get_target(self):
        if self.target_question:
            return self.target_question

        elif self.target_item:
            return self.target_item

        else:
            raise ValidationError('No target question or target item specified.')

    def get_related_project(self):
        target = self.get_target()
        if isinstance(target, QuestionBase):
            return target.project

        elif isinstance(target, QuestionItem):
            return target.question.project

        else:
            return None

    def get_source(self):
        """
        Returns the filter source.

        Returns:
        - the related model instance if the filter source is a Question or
            a QuestionItem.
        - the source_identifier (usually a variable name) for other source types.
        - None, if the source does not exist anymore.
        """
        if self.source_type == FilterSourceTypes.QUESTION:
            source = self.source_question
            return source

        elif self.source_type == FilterSourceTypes.QUESTION_ITEM:
            source = self.source_item
            return source

        elif self.source_type == FilterSourceTypes.URL_PARAMETER:
            system_variables = get_url_parameters(self.get_related_project())
            if self.source_identifier in system_variables.keys():
                return self.source_identifier
            else:
                return None

        elif self.source_type == FilterSourceTypes.SYSTEM:
            return self.source_identifier

        elif self.source_type == FilterSourceTypes.PARTICIPANT:
            participant_variables = get_participant_variables(self.get_related_project())
            if self.source_identifier in participant_variables.keys():
                return self.source_identifier
            else:
                return None

        elif self.source_type == FilterSourceTypes.DONATION:
            return self.source_identifier

        else:
            raise ValidationError('No valid source specified.')

    def get_source_name(self):
        """
        Helper function to display source name in UI.
        """
        source = self.get_source()
        if isinstance(source, QuestionBase) or isinstance(source, QuestionItem):
            return source.variable_name
        else:
            return source

    def check_source_exists(self):
        source = self.get_source()
        if source is not None:
            return True
        else:
            self.source_exists = False
            self.index = -1 * int(datetime.now().timestamp())
            self.save()
            return False

    def clean(self):
        # Clean targets
        fk_targets = [self.target_question, self.target_item]
        non_null_fks = [s for s in fk_targets if s is not None]

        if len(non_null_fks) > 1:
            raise ValidationError('Only one target type can be specified')

        if len(non_null_fks) == 0 and not self.source_identifier:
            raise ValidationError('A target must be specified')

        # Get source question or item (if applicable).
        if self.source_type in [FilterSourceTypes.QUESTION, FilterSourceTypes.QUESTION_ITEM]:

            if self.source_type == FilterSourceTypes.QUESTION:
                self.source_question = QuestionBase.objects.get(pk=self.source_identifier)
                self.source_item = None

            elif self.source_type == FilterSourceTypes.QUESTION_ITEM:
                self.source_question = None
                self.source_item = QuestionItem.objects.get(pk=self.source_identifier)

        # Restrict comparison operators for non-numeric open questions.
        if isinstance(self.source_question, OpenQuestion):
            if self.source_question.input_type != OpenQuestion.InputTypes.NUMBER:
                if self.condition_operator in ['>', '<', '>=', '<=']:
                    raise ValidationError(
                        f'Operator "{self.condition_operator}" is not valid for '
                        f'open questions with non-numeric inputs.'
                    )

    def get_source_config_id(self):
        """
        Get the ID of the filter's source as used in config dictionaries.

        Returns:
            str: The config ID of the filter's source.
        """
        if self.source_type == FilterSourceTypes.QUESTION:
            return get_filter_config_id(self.source_question)
        elif self.source_type == FilterSourceTypes.QUESTION_ITEM:
            return get_filter_config_id(self.source_item)
        else:
            return self.source_identifier

    def get_target_config_id(self):
        """
        Get the ID of the filter's target as used in config dictionaries.

        Returns:
            str: The config ID of the filter's target.
        """
        if self.target_question:
            return get_filter_config_id(self.target_question)
        elif self.target_item:
            return get_filter_config_id(self.target_item)


def get_filter_config_id(obj: Union[QuestionBase, QuestionItem]) -> str:
    """
    Returns the passed objects ID used for the filter configuration.

    Args:
        obj (QuestionBase | QuestionItem): Either a QuestionBase or a
            QuestionItem instance.

    Returns:
        str: 'question-<question.pk> for a QuestionBase or
            'item-<item.pk>' for a QuestionItem.
    """
    if isinstance(obj, QuestionItem):
        return f'{FilterSourceTypes.QUESTION_ITEM}-{obj.pk}'
    else:
        return f'{FilterSourceTypes.QUESTION}-{obj.pk}'
