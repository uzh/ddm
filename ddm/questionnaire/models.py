from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from ddm.encryption.models import ModelWithEncryptedData
from ddm.projects.service import get_participant_variables, get_url_parameters
from ddm.questionnaire.constants import FilterSourceTypes

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from ddm.projects.models import DonationProject


class FilterConditionMixin:
    """
    Mixin adding utility functions to models with a generic relationship to
    FilterConditions.
    """

    def get_active_filters(self) -> QuerySet[FilterCondition]:
        """
        Returns the set of associated filters that are still active.

        Also used in templates.

        Returns:
            queryset
        """
        return self.filtercondition_set.filter(source_exists=True).order_by("index")


class QuestionType(models.TextChoices):
    GENERIC = "generic", "Generic Question"
    SINGLE_CHOICE = "single_choice", "Single Choice Question"
    MULTI_CHOICE = "multi_choice", "Multi Choice Question"
    MATRIX = "matrix", "Matrix Question"
    SEMANTIC_DIFF = "semantic_diff", "Semantic Differential"
    OPEN = "open", "Open Question"
    TRANSITION = "transition", "Text Block"


class QuestionBase(FilterConditionMixin, PolymorphicModel):
    project = models.ForeignKey(
        "ddm_projects.DonationProject", on_delete=models.CASCADE
    )
    blueprint = models.ForeignKey(
        "ddm_datadonation.DonationBlueprint",
        on_delete=models.CASCADE,
        # TODO: Set this to a different policy; possibly add a "active"
        #  attribute to question and set inactive. If changed, update
        #  blueprint delete view.
        null=True,
        blank=True,
    )

    DEFAULT_QUESTION_TYPE = QuestionType.GENERIC
    question_type = models.CharField(
        max_length=20, blank=False, choices=QuestionType, default=DEFAULT_QUESTION_TYPE
    )

    name = models.CharField(max_length=255)
    page = models.PositiveIntegerField(default=1, verbose_name="Page")
    index = models.PositiveIntegerField(default=1, verbose_name="Index")

    variable_name = models.SlugField(
        max_length=50,
        null=False,
        verbose_name="Variable name for storing response",
        help_text=(
            "Will be used in the data export to identify responses to this question."
        ),
    )

    text = models.TextField(
        blank=True,
        help_text=(
            "If a question is linked to a File Blueprint, data points from the "
            "donated data associated with the linked donation blueprint can be "
            "included in the question text. "
            'This data can be included as "{{ data }}" in the question text. '
            "It is possible to subset the data object (e.g., to include the last "
            "datapoint you can use {{ data.0 }} or include advanced "
            "rendering options included in the Django templating engine. "
            "For a more comprehensive overview and examples see the documentation. "
            "Additionally, information directly related to the participant can "
            "be included in the question text. "
            'This information can be referenced as "{{ participant }}".'
        ),
    )

    class RequirementLevel(models.TextChoices):
        NOT_REQUIRED = "not_required", "Not required"
        SOFT_REQUIRED = "soft_required", "Soft"
        HARD_REQUIRED = "hard_required", "Hard"

    requirement_level = models.CharField(
        max_length=20,
        blank=False,
        choices=RequirementLevel.choices,
        default=RequirementLevel.NOT_REQUIRED,
        help_text=(
            "Not required: a response is optional. "
            "Soft: if missing, a warning is shown once but can be dismissed. "
            "Hard: a response is required before proceeding."
        ),
    )

    class Meta:
        ordering = ["page", "index"]
        constraints = [
            models.UniqueConstraint(
                fields=["variable_name", "project"], name="unique_varname_per_project"
            ),
        ]

    def __init__(self, *args, **kwargs) -> None:
        if not args:
            kwargs["question_type"] = self.DEFAULT_QUESTION_TYPE
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Validate uniqueness before saving to avoid database IntegrityError."""
        if (
            QuestionBase.objects.filter(
                variable_name=self.variable_name, project=self.project
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            e_msg = {
                "variable_name": (
                    "A variable with this name already exists in the project."
                )
            }
            raise ValidationError(e_msg)

    def save(self, *args, **kwargs) -> None:
        """Call clean() before saving to avoid possible database IntegrityError."""
        self.clean()
        super().save(*args, **kwargs)

    def is_general(self) -> bool:
        return self.blueprint is None

    def get_response_keys(self) -> list:
        return []

    def get_valid_responses(self) -> list:
        """Returns a list of valid responses for this question."""
        return [-99, -77]

    def validate_response(self, response_key: str, response: Any) -> bool:  # noqa: ANN401
        """Placeholder method - must be defined in derivative models."""
        return True


class ItemMixin(models.Model):
    randomize_items = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def get_response_keys(self) -> list[str]:
        item_pks = self.questionitem_set.all().values_list("pk", flat=True)
        return [f"item-{pk}" for pk in list(item_pks)]


class ScaleMixin:
    def get_valid_responses(self) -> list:
        valid_responses = super().get_valid_responses()
        valid_responses += list(
            self.scalepoint_set.all().values_list("value", flat=True)
        )
        return valid_responses


class SingleChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SINGLE_CHOICE

    def get_response_keys(self) -> list[str]:
        return [f"question-{self.pk}"]

    def get_valid_responses(self) -> list:
        """
        Valid response values include all related item values
        (QuestionItem.value) plus -99 which indicates that a question was not
        answered/skipped.
        """
        valid_responses = super().get_valid_responses()
        item_values = self.questionitem_set.all().values_list("value", flat=True)
        valid_responses += list(item_values)
        return valid_responses


class MultiChoiceQuestion(ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MULTI_CHOICE

    def get_valid_responses(self) -> list:
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
        SMALL = "small", "Small"
        LARGE = "large", "Large"

    display = models.CharField(
        max_length=20,
        blank=False,
        choices=DisplayOptions.choices,
        default=DisplayOptions.SMALL,
        help_text='"Small" displays a one-line textfield, "Large" a multiline '
        "textfield as input.",
    )

    class InputTypes(models.TextChoices):
        TEXT = "text", "Any text"
        NUMBER = "numbers", "Numbers only"
        EMAIL = "email", "Email address"

    input_type = models.CharField(
        max_length=20,
        blank=False,
        choices=InputTypes.choices,
        default=InputTypes.TEXT,
        verbose_name="Input type",
        help_text="Select the type of input allowed.",
    )

    min_input_length = models.PositiveIntegerField(
        verbose_name="Minimum input length",
        help_text=(
            "Participants' input must be of at least this length. If empty, "
            "no minimal input length restriction is enforced."
        ),
        blank=True,
        null=True,
        default=None,
    )

    max_input_length = models.PositiveIntegerField(
        verbose_name="Maximum input length",
        help_text=(
            "Participants' input cannot exceed this length. If empty, "
            "no input length restriction is enforced."
        ),
        blank=True,
        null=True,
        default=None,
    )

    min_number_value = models.IntegerField(
        verbose_name="Minimum input value",
        help_text=(
            "Participants must enter a number greater than or equal to this value. "
            "If empty, no minimum input value restriction is enforced."
        ),
        blank=True,
        null=True,
        default=None,
    )

    max_number_value = models.IntegerField(
        verbose_name="Maximum input value",
        help_text=(
            "Participants must enter a number less than or equal to this value. "
            "If empty, no maximum input value restriction is enforced."
        ),
        blank=True,
        null=True,
        default=None,
    )

    multi_item_response = models.BooleanField(default=False)

    def clean(self) -> None:
        super().clean()

        if (
            self.min_input_length is not None
            and self.max_input_length is not None
            and self.min_input_length > self.max_input_length
        ):
            e_msg = "Minimum input length cannot be greater than maximum input length."
            raise ValidationError(
                {
                    "min_input_length": e_msg,
                    "max_input_length": e_msg,
                }
            )

        if (
            self.min_number_value is not None
            and self.max_number_value is not None
            and self.min_number_value > self.max_number_value
        ):
            e_msg = "Minimum input value cannot be greater than maximum input value."
            raise ValidationError(
                {
                    "min_number_value": e_msg,
                    "max_number_value": e_msg,
                }
            )

    def get_response_keys(self) -> list[str]:
        if self.multi_item_response:
            item_pks = self.questionitem_set.all().values_list("pk", flat=True)
            return [f"item-{pk}" for pk in list(item_pks)]
        return [f"question-{self.pk}"]

    def get_valid_responses(self) -> list:
        valid_responses = super().get_valid_responses()
        valid_responses += ["__any_string__"]
        return valid_responses


class MatrixQuestion(ScaleMixin, ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.MATRIX

    show_scale_headings = models.BooleanField(default=False)

    def get_valid_responses(self) -> list:
        return super().get_valid_responses()


class SemanticDifferential(ScaleMixin, ItemMixin, QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.SEMANTIC_DIFF

    def get_valid_responses(self) -> list:
        return super().get_valid_responses()


class Transition(QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionType.TRANSITION


class QuestionItem(FilterConditionMixin, models.Model):
    question = models.ForeignKey("QuestionBase", on_delete=models.CASCADE)
    index = models.IntegerField()
    label = models.CharField(max_length=255, blank=True)
    label_alt = models.CharField(max_length=255, blank=True, verbose_name="Label Right")
    value = models.IntegerField()
    randomize = models.BooleanField(default=False)

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(
                fields=["index", "question"], name="unique_item_index_per_question"
            ),
            models.UniqueConstraint(
                fields=["value", "question"], name="unique_item_value_per_question"
            ),
        ]

    def __str__(self) -> str:
        return f"Question Item '{self.label}' (question: {self.question.pk})"

    @property
    def variable_name(self) -> str:
        return f"{self.question.variable_name}-{self.value}"


class ScalePoint(models.Model):
    question = models.ForeignKey("QuestionBase", on_delete=models.CASCADE)
    index = models.IntegerField()

    input_label = models.CharField(max_length=100, blank=True)

    heading_label = models.CharField(max_length=100, blank=True)

    value = models.IntegerField()
    secondary_point = models.BooleanField(default=False)

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(
                fields=["index", "question"], name="unique_index_per_question"
            ),
        ]

    def __str__(self) -> str:
        return f"Scale Point {self.pk}"


class QuestionnaireResponse(ModelWithEncryptedData):
    # Will only ever be deleted, when the project is deleted.
    project = models.ForeignKey(
        "ddm_projects.DonationProject", on_delete=models.CASCADE
    )
    participant = models.ForeignKey(
        "ddm_participation.Participant", on_delete=models.CASCADE
    )
    time_submitted = models.DateTimeField(default=timezone.now)
    data = models.BinaryField()  # Holds the actual response data (encrypted)
    questionnaire_config = models.JSONField(default=list, null=True)
    # Holds the questionnaire configuration at the time of participation.

    is_complete = models.BooleanField(default=True)
    # False while responses are saved incrementally as the participant
    # progresses through the questionnaire; set True on final submission.

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "participant"],
                name="unique_questionnaireresponse_per_participant",
            ),
        ]


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
        "QuestionBase", on_delete=models.CASCADE, null=True, blank=True
    )
    target_item = models.ForeignKey(
        "QuestionItem", on_delete=models.CASCADE, null=True, blank=True
    )

    # Source configuration
    source_question = models.ForeignKey(
        "QuestionBase",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dependent_filters",
    )
    source_item = models.ForeignKey(
        "QuestionItem",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dependent_filters",
    )

    source_type = models.CharField(
        max_length=60,
        choices=FilterSourceTypes.choices,
    )
    source_identifier = models.CharField(max_length=255, blank=True)

    index = models.IntegerField(default=1)

    class ConditionCombinators(models.TextChoices):
        AND = "AND", "AND"
        OR = "OR", "OR"

    combinator = models.CharField(
        max_length=3,
        choices=ConditionCombinators.choices,
        default=ConditionCombinators.AND,
        help_text=(
            "Defines whether all conditions (AND) or any (OR) must be met."
            "In the filter condition with the lowest index, this will be "
            "ignored. The conditions following will be evaluated as a chain, "
            "where AND has higher precedence than OR. E.g., Condition1 OR "
            "Condition2 AND Condition3 OR Condition4 will be evaluated as "
            '"Condition1 OR (Condition2 AND Condition3) OR Condition4".'
        ),
    )

    class ConditionOperators(models.TextChoices):
        EQUALS = "==", "Equal (==)"
        EQUALS_NOT = "!=", "Not Equal (!=)"
        GREATER_THAN = ">", "Greater than (>)"
        SMALLER_THAN = "<", "Smaller than (<)"
        GREATER_OR_EQUAL_THAN = ">=", "Greater than or equal (>=)"
        SMALLER_OR_EQUAL_THAN = "<=", "Smaller than or equal (<=)"
        CONTAINS = "contains", "Contains"
        CONTAINS_NOT = "contains_not", "Does not Contain"

    condition_operator = models.CharField(
        max_length=20,
        choices=ConditionOperators.choices,
        default=ConditionOperators.EQUALS,
        help_text="The condition operator for filtering.",
    )

    condition_value = models.JSONField(
        blank=True,
        null=True,
        help_text="The value to compare the source's value against.",
    )

    source_exists = models.BooleanField(default=True)
    # Is set to false if non-fk source does not exist anymore.

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["target_item", "target_question", "index"],
                name="unique_index_per_target",
            )
        ]

    def __str__(self) -> str:
        return f"Filter Condition {self.pk}"

    def get_target(self) -> QuestionBase | QuestionItem:
        if self.target_question:
            return self.target_question

        if self.target_item:
            return self.target_item

        e_msg = "No target question or target item specified."
        raise ValidationError(e_msg)

    def get_related_project(self) -> DonationProject:
        target = self.get_target()
        if isinstance(target, QuestionBase):
            return target.project

        if isinstance(target, QuestionItem):
            return target.question.project

        e_msg = f"Expected Question or QuestionItem, got {type(target).__name__}"
        raise ValueError(e_msg)

    def get_source(self) -> QuestionBase | QuestionItem | str | None:
        """
        Returns the filter source.

        Returns:
        - the related model instance if the filter source is a Question or
            a QuestionItem.
        - the source_identifier (usually a variable name) for other source types.
        - None, if the source does not exist anymore.
        """
        match self.source_type:
            case FilterSourceTypes.QUESTION:
                return self.source_question

            case FilterSourceTypes.QUESTION_ITEM:
                return self.source_item

            case FilterSourceTypes.URL_PARAMETER:
                system_variables = get_url_parameters(self.get_related_project())
                source_id = self.source_identifier
                return source_id if source_id in system_variables else None

            case FilterSourceTypes.SYSTEM:
                return self.source_identifier

            case FilterSourceTypes.PARTICIPANT:
                participant_variables = get_participant_variables()
                source_id = self.source_identifier
                return source_id if source_id in participant_variables else None

            case FilterSourceTypes.DONATION:
                # TODO: Add variable check similar to PARTICIPANT and
                #  URL_PARAMETER variables.
                return self.source_identifier

            case _:
                e_msg = "No valid source specified."
                raise ValidationError(e_msg)

    def get_source_name(self) -> str | None:
        """Helper function to display source name in UI."""
        source = self.get_source()
        if isinstance(source, (QuestionBase, QuestionItem)):
            return source.variable_name
        return source

    def check_source_exists(self) -> bool:
        source = self.get_source()
        if source is not None:
            return True
        self.source_exists = False
        self.index = -1 * int(timezone.now().timestamp())
        self.save()
        return False

    def clean(self) -> None:
        # Clean targets
        fk_targets = [self.target_question, self.target_item]
        non_null_fks = [s for s in fk_targets if s is not None]

        if len(non_null_fks) > 1:
            e_msg = "Only one target type can be specified"
            raise ValidationError(e_msg)

        if len(non_null_fks) == 0 and not self.source_identifier:
            e_msg = "A target must be specified"
            raise ValidationError(e_msg)

        # Get source question or item (if applicable).
        if self.source_type in [
            FilterSourceTypes.QUESTION,
            FilterSourceTypes.QUESTION_ITEM,
        ]:
            if self.source_type == FilterSourceTypes.QUESTION:
                self.source_question = QuestionBase.objects.get(
                    pk=self.source_identifier
                )
                self.source_item = None

            elif self.source_type == FilterSourceTypes.QUESTION_ITEM:
                self.source_question = None
                self.source_item = QuestionItem.objects.get(pk=self.source_identifier)

        # Restrict comparison operators for non-numeric open questions.
        if isinstance(self.source_question, OpenQuestion):
            if self.source_question.input_type != OpenQuestion.InputTypes.NUMBER:
                if self.condition_operator in [">", "<", ">=", "<="]:
                    e_msg = (
                        f'Operator "{self.condition_operator}" is not valid for '
                        f"open questions with non-numeric inputs."
                    )
                    raise ValidationError(e_msg)
