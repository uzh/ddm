import uuid
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Model, QuerySet
from django.forms import Form, inlineformset_factory
from django.utils.safestring import mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget

from ddm.projects.models import DonationProject
from ddm.projects.service import (
    get_donation_variables,
    get_participant_variables,
    get_url_parameters,
)
from ddm.questionnaire.constants import FilterSourceTypes, QuestionType
from ddm.questionnaire.models import (
    FilterCondition,
    MatrixQuestion,
    MultiChoiceQuestion,
    OpenQuestion,
    QuestionBase,
    QuestionItem,
    ScalePoint,
    SemanticDifferential,
    SingleChoiceQuestion,
    Transition,
)

QUESTION_CLASSES = {
    "single_choice": SingleChoiceQuestion,
    "multi_choice": MultiChoiceQuestion,
    "open": OpenQuestion,
    "matrix": MatrixQuestion,
    "semantic_diff": SemanticDifferential,
    "transition": Transition,
}

_SHARED_FIELDS = [
    "name",
    "variable_name",
    "page",
    "index",
    "text",
    "blueprint",
    "required",
]

QUESTION_FIELDS = {
    "single_choice": [*_SHARED_FIELDS, "randomize_items"],
    "multi_choice": [*_SHARED_FIELDS, "randomize_items"],
    "matrix": [*_SHARED_FIELDS, "randomize_items", "show_scale_headings"],
    "semantic_diff": [*_SHARED_FIELDS, "randomize_items"],
    "open": [
        *_SHARED_FIELDS,
        "input_type",
        "max_input_length",
        "display",
        "multi_item_response",
        "randomize_items",
    ],
    "transition": _SHARED_FIELDS,
}

EXCLUDED_FIELDS = {
    "transition": ["required", "variable_name"],
}

HELP_TEXTS = {
    "name": "For internal use",
    "variable_name": "Used to identify responses in data exports",
    "text": "",
    "required": (
        "If required questions are left unanswered, participants see "
        'a warning when clicking "Next". '
        'They can proceed by clicking "Next" again.'
    ),
    "blueprint": mark_safe(
        "If linked to a Blueprint, the donated data linked to this Blueprint "
        "can be included in the question text. "
        '<span class="fw-bold ps-2">Important:</span> If no donated data is '
        "linked to the Blueprint the question will not be shown to a participant "
        "(e.g., because no consent was given or no data was extracted)."
    ),
    "multi_item_response": "Control if its one text field to respond or multiple",
    "randomize_items": mark_safe(
        "If enabled, <strong>all</strong> items will be displayed in "
        "random order. If only certain items should be positioned randomly, "
        "use the <code>randomize</code> option on the item-level."
    ),
    "display": mark_safe(
        "<code>Small</code> displays a one-line textfield, "
        "<code>Large</code> a multiline textfield as input."
    ),
}

LABELS = {
    "blueprint": "Linked Blueprint",
    "randomize_items": "Randomize item order",
    "index": "Position",
    "show_scale_headings": "Show scale column headings",
    "variable_name": "Variable name",
}

EMPTY_LABELS = {
    "blueprint": "-",
    "page": "Select a page",
}

WIDGETS = {
    "text": CKEditor5Widget(config_name="ddm_ckeditor_temp_func"),
}


class BaseQuestionForm(forms.ModelForm):
    """Shared behavior for all question type forms."""

    _empty_labels: dict = {}
    _question_type: str = ""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field_name, empty_label in self._empty_labels.items():
            if field_name in self.fields:
                self.fields[field_name].empty_label = empty_label

    def save(self, commit: bool = True) -> Model:  # noqa: FBT002
        if self._question_type == "transition" and not self.instance.variable_name:
            self.instance.variable_name = f"_textblock_{uuid.uuid4().hex[:8]}"
        return super().save(commit=commit)


def get_question_form(question_type: str) -> type[BaseQuestionForm]:
    fields = [
        f
        for f in QUESTION_FIELDS[question_type]
        if f not in EXCLUDED_FIELDS.get(question_type, [])
    ]
    empty_labels = {k: v for k, v in EMPTY_LABELS.items() if k in fields}

    form_class = forms.modelform_factory(
        QUESTION_CLASSES[question_type],
        form=BaseQuestionForm,
        fields=fields,
        help_texts={k: v for k, v in HELP_TEXTS.items() if k in fields},
        labels={k: v for k, v in LABELS.items() if k in fields},
        widgets={k: v for k, v in WIDGETS.items() if k in fields},
    )
    form_class._empty_labels = empty_labels  # noqa: SLF001
    form_class._question_type = question_type  # noqa: SLF001
    return form_class


class QuestionItemForm(forms.ModelForm):
    class Meta:
        model = QuestionItem
        fields = [
            "index",
            "label",
            "label_alt",
            "value",
            "randomize",
        ]

        labels = {
            "index": "Position",
            "label": "Item text",
            "label_alt": "Item text (right)",
        }

        widgets = {
            "label": forms.Textarea(attrs={"rows": 2}),
            "label_alt": forms.Textarea(attrs={"rows": 1}),
        }


class BaseQuestionItemFormset(forms.BaseInlineFormSet):
    def __init__(self, *args, show_label_alt: bool = True, **kwargs) -> None:
        self.show_label_alt = show_label_alt
        super().__init__(*args, **kwargs)

    def _customize_form(self, form: Form) -> Form:
        """Conditionally show/hide secondary label."""
        if not self.show_label_alt:
            form.fields.pop("label_alt", None)
        else:
            form.fields["label"].widget = forms.Textarea(attrs={"rows": 1})
        return form

    def _construct_form(self, i, **kwargs):  # noqa: ANN001, ANN202
        return self._customize_form(super()._construct_form(i, **kwargs))

    @property
    def empty_form(self) -> Form:
        return self._customize_form(super().empty_form)


QuestionItemInlineFormset = inlineformset_factory(
    QuestionBase,
    QuestionItem,
    form=QuestionItemForm,
    formset=BaseQuestionItemFormset,
    extra=0,
)


class ScalePointForm(forms.ModelForm):
    class Meta:
        model = ScalePoint
        fields = [
            "index",
            "value",
            "input_label",
            "heading_label",
            "secondary_point",
        ]

        labels = {
            "index": "Position",
            "input_label": "Label",
            "secondary_point": "Extra option",
            "heading_label": "Column heading",
        }


ScalePointInlineFormset = inlineformset_factory(
    QuestionBase, ScalePoint, form=ScalePointForm, extra=0
)


class FilterConditionForm(forms.ModelForm):
    source = forms.ChoiceField(
        choices=[],
        label="Compare to",
        required=True,
        widget=forms.Select(attrs={"class": "w-100"}),
    )
    condition_operator = forms.ChoiceField(
        choices=[],
        label="Operator",
        required=True,
        widget=forms.Select(attrs={"class": "w-100"}),
    )
    combinator = forms.ChoiceField(
        choices=[],
        label="Logic",
        required=True,
        widget=forms.Select(attrs={"class": "w-100"}),
    )
    condition_value = forms.CharField(
        label="Value",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    source_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    source_identifier = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = FilterCondition
        fields = [
            "index",
            "combinator",
            "source",
            "condition_operator",
            "condition_value",
            "source_type",
            "source_identifier",
        ]

    def __init__(
        self,
        *args,
        project: DonationProject,
        target_object: QuestionBase | QuestionItem,
        **kwargs,
    ) -> None:
        """
        Dynamically filter the object ID dropdowns based on ContentType selection.
        """
        super().__init__(*args, **kwargs)

        self.project = project
        self.target_object = target_object
        self.question_id = self._get_question_id()

        self._setup_choices()
        self._set_initial_values()

    # --- Setup methods ---

    def _get_question_id(self) -> int:
        if isinstance(self.target_object, QuestionItem):
            return self.target_object.question.id
        return self.target_object.id

    def _setup_choices(self) -> None:
        """Configure all dropdown choices."""
        item_set = self._get_item_sources()
        question_set = self._get_question_sources()

        self.fields["source"].choices = [
            ("", "Select variable..."),
            *self._build_source_choices(question_set, item_set),
        ]
        self.fields["condition_operator"].choices = [
            ("", "Select operator..."),
            *FilterCondition.ConditionOperators.choices,
        ]
        self.fields["combinator"].choices = [
            ("", "Select logic..."),
            *FilterCondition.ConditionCombinators.choices,
        ]

    def _set_initial_values(self) -> None:
        """Set initial form values for existing instances."""
        if not self.instance.pk:
            return

        source_id = (
            self.instance.source_question_id
            or self.instance.source_item_id
            or self.instance.source_identifier
        )
        self.initial["source"] = f"{self.instance.source_type}-{source_id}"

    # --- Source querysets ---

    def _get_item_sources(self) -> QuerySet[QuestionItem]:
        """Get QuestionItems available as filter sources.

        Exclude items that:
        -   are related to the same question as the target of the filter condition.
        -   are single choice items.
        """
        return (
            QuestionItem.objects.filter(question__project=self.project)
            .exclude(question__id=self.question_id)
            .exclude(question__question_type=QuestionType.SINGLE_CHOICE)
            .select_related("question")
        )

    def _get_question_sources(self) -> QuerySet[QuestionBase]:
        """Get the set of questions available as choices in the source field.

        Exclude questions:
        -   where the response is only recorded in relation to the items.
        """
        excluded_types = [
            QuestionType.GENERIC,
            QuestionType.TRANSITION,
            QuestionType.MULTI_CHOICE,
            QuestionType.MATRIX,
            QuestionType.SEMANTIC_DIFF,
        ]

        # Base Queryset
        questions = (
            QuestionBase.objects.filter(project=self.project)
            .exclude(id=self.question_id)
            .exclude(question_type__in=excluded_types)
        )

        open_questions_with_items = (
            OpenQuestion.objects.filter(multi_item_response=True)
            .exclude(id=self.question_id)
            .values_list("id", flat=True)
        )
        return questions.exclude(id__in=open_questions_with_items)

    # --- Choice building ---

    def _build_source_choices(
        self, question_set: QuerySet[QuestionBase], item_set: QuerySet[QuestionItem]
    ) -> list[tuple[str, str]]:
        """Build and sort all source choices."""

        question_choices = [(FilterSourceTypes.QUESTION, q) for q in question_set]
        item_choices = [(FilterSourceTypes.QUESTION_ITEM, i) for i in item_set]
        combined = question_choices + item_choices

        # Sort by page and index
        combined = sorted(
            combined,
            key=lambda pair: (
                pair[1].page if hasattr(pair[1], "page") else pair[1].question.page,
                pair[1].index,
            ),
        )

        # Add other variable sources
        type_var_mapping = [
            (FilterSourceTypes.URL_PARAMETER, lambda: get_url_parameters(self.project)),
            (FilterSourceTypes.PARTICIPANT, get_participant_variables),
            (FilterSourceTypes.DONATION, get_donation_variables),
        ]

        for source_type, get_vars in type_var_mapping:
            combined.extend((source_type, v) for v in get_vars())

        return [self._create_source_label(src_type, obj) for src_type, obj in combined]

    @staticmethod
    def _get_question_item_label(item: QuestionItem) -> str:
        name = item.variable_name
        if not item.label:
            return name

        max_label_length = 30
        if len(item.label) < max_label_length:
            label = item.label
        else:
            label = item.label[:max_label_length] + "..."
        return f"{name} ({label})"

    def _create_source_label(
        self, source_type: FilterSourceTypes, obj: QuestionBase | QuestionItem | str
    ) -> tuple[str, str]:
        """Create a single (value, label) choice tuple."""
        label_templates = {
            FilterSourceTypes.QUESTION: {
                "id": lambda o: o.id,
                "prefix": lambda o: f"[question, p{o.page}]",
                "label": lambda o: o.variable_name,
            },
            FilterSourceTypes.QUESTION_ITEM: {
                "id": lambda o: o.id,
                "prefix": lambda o: f"[item, p{o.question.page}]",
                "label": lambda o: self._get_question_item_label(o),  # noqa: PLW0108
            },
            FilterSourceTypes.URL_PARAMETER: {
                "id": lambda o: o,
                "prefix": lambda o: "[url]",
                "label": lambda o: o,
            },
            FilterSourceTypes.PARTICIPANT: {
                "id": lambda o: o,
                "prefix": lambda o: "[participant]",
                "label": lambda o: o,
            },
            FilterSourceTypes.DONATION: {
                "id": lambda o: o,
                "prefix": lambda o: "[donation]",
                "label": lambda o: o,
            },
        }

        label_config = label_templates.get(source_type)
        if not label_config:
            e_msg = f"Unknown source type: {source_type}"
            raise ValueError(e_msg)

        value = f"{source_type}-{label_config['id'](obj)}"
        label = f"{label_config['prefix'](obj)} {label_config['label'](obj)}"
        return value, label

    # --- Validation and saving ---

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        source = cleaned_data.get("source")

        if not source:
            e_msg = "Please select a comparison variable."
            raise ValidationError(e_msg)

        try:
            source_type, source_id = source.split("-", 1)
        except ValueError as e:
            e_msg = "Invalid source format."
            raise ValidationError(e_msg) from e

        # Validate source exists
        self._validate_source(source_type, source_id)

        cleaned_data["source_type"] = source_type
        cleaned_data["source_identifier"] = source_id
        return cleaned_data

    @staticmethod
    def _validate_source(source_type: type, source_id: int) -> None:
        """Validate that the source object exists."""
        if source_type == FilterSourceTypes.QUESTION:
            if not QuestionBase.objects.filter(pk=source_id).exists():
                e_msg = "Selected question not found."
                raise ValidationError(e_msg)
        elif source_type == FilterSourceTypes.QUESTION_ITEM:
            if not QuestionItem.objects.filter(pk=source_id).exists():
                e_msg = "Selected item not found."
                raise ValidationError(e_msg)

    def save(self, commit: bool = True) -> Model:  # noqa: FBT002
        instance = super().save(commit=False)
        source_type, source_id = self.cleaned_data["source"].split("-", 1)

        # Reset all source fields
        instance.source_question = None
        instance.source_item = None
        instance.source_identifier = None
        instance.source_type = source_type

        # Set the appropriate source field
        if source_type == FilterSourceTypes.QUESTION:
            instance.source_question = QuestionBase.objects.get(pk=source_id)
        elif source_type == FilterSourceTypes.QUESTION_ITEM:
            instance.source_item = QuestionItem.objects.get(pk=source_id)
        else:
            instance.source_identifier = source_id

        if commit:
            instance.save()
        return instance
