import uuid

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.safestring import mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget

from ddm.projects.service import (
    get_url_parameters, get_participant_variables, get_donation_variables
)
from ddm.questionnaire.models import (
    FilterCondition,
    MatrixQuestion,
    MultiChoiceQuestion,
    OpenQuestion,
    QuestionBase,
    QuestionItem,
    SemanticDifferential,
    SingleChoiceQuestion,
    Transition, ScalePoint
)
from ddm.questionnaire.constants import FilterSourceTypes, QuestionType


def get_question_form(question_type):
    QUESTION_CLASSES = {
        'single_choice': SingleChoiceQuestion,
        'multi_choice': MultiChoiceQuestion,
        'open': OpenQuestion,
        'matrix': MatrixQuestion,
        'semantic_diff': SemanticDifferential,
        'transition': Transition
    }

    SHARED_FIELDS = [
        'name',
        'variable_name',
        'page',
        'index',
        'text',
        'blueprint',
        'required',
    ]

    QUESTION_FIELDS = {
        'single_choice': SHARED_FIELDS + ['randomize_items'],
        'multi_choice': SHARED_FIELDS + ['randomize_items'],
        'matrix': SHARED_FIELDS + ['randomize_items', 'show_scale_headings'],
        'semantic_diff': SHARED_FIELDS + ['randomize_items'],
        'open': SHARED_FIELDS + [
            'input_type',
            'max_input_length',
            'display',
            'multi_item_response',
            'randomize_items'
        ],
        'transition': SHARED_FIELDS
    }

    HELP_TEXTS = {
        'name': 'For internal use',
        'variable_name': 'Used to identify responses in data exports',
        'text': '',
        'required': (
            'If required questions are left unanswered, participants see '
            'a warning when clicking "Next". '
            'They can proceed by clicking "Next" again.'
        ),
        'blueprint': mark_safe(
            'If linked to a Blueprint, the donated data linked to this Blueprint '
            'can be included in the question text. '
            '<span class="fw-bold ps-2">Important:</span> If no donated data is linked to the '
            'Blueprint the question will not be shown to a participant '
            '(e.g., because no consent was given or no data was extracted).'
        ),
        'multi_item_response': (
            'Control if its one text field to respond or multiple'
        ),
        'randomize_items': mark_safe(
            'If enabled, <strong>all</strong> items will be displayed in '
            'random order. If only certain items should be positioned randomly, '
            'use the <code>randomize</code> option on the item-level.'
        ),
        'display': mark_safe(
            '<code>Small</code> displays a one-line textfield, '
            '<code>Large</code> a multiline textfield as input.'
        )
    }

    LABELS = {
        'blueprint': 'Linked Blueprint',
        'randomize_items': 'Randomize item order',
        'index': 'Position',
        'show_scale_headings': 'Show scale column headings',
        'variable_name': 'Variable name'
    }

    EMPTY_LABELS = {
        'blueprint': '-',
        'page': 'Select a page',
    }

    WIDGETS = {
        'text': CKEditor5Widget(config_name='ddm_ckeditor_temp_func'),
    }

    _fields = QUESTION_FIELDS[question_type]
    if question_type == 'transition':
        _fields = [f for f in _fields if f not in ['required', 'variable_name']]

    _help_texts = {k: v for k, v in HELP_TEXTS.items() if k in _fields}
    _labels = {k: v for k, v in LABELS.items() if k in _fields}

    _empty_labels = {k: v for k, v in EMPTY_LABELS.items() if k in _fields}

    _widgets = {k: v for k, v in WIDGETS.items() if k in _fields}

    class QuestionForm(forms.ModelForm):
        class Meta:
            model = QUESTION_CLASSES[question_type]
            fields = _fields
            help_texts = _help_texts
            labels = _labels
            widgets = _widgets

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field_name, empty_label in _empty_labels.items():
                if field_name in self.fields:
                    self.fields[field_name].empty_label = empty_label

        def save(self, commit=True):
            if question_type == 'transition' and not self.instance.variable_name:
                self.instance.variable_name = f'_textblock_{uuid.uuid4().hex[:8]}'
            return super().save(commit=commit)

    return QuestionForm


class QuestionItemForm(forms.ModelForm):

    class Meta:
        model = QuestionItem
        fields = [
            'index',
            'label',
            'label_alt',
            'value',
            'randomize',
        ]

        labels = {
            'index': 'Position',
            'label': 'Item text',
            'label_alt': 'Item text (right)',
        }

        widgets = {
            'label': forms.Textarea(attrs={'rows': 2}),
            'label_alt': forms.Textarea(attrs={'rows': 1}),
        }


class BaseQuestionItemFormset(forms.BaseInlineFormSet):
    def __init__(self, *args, show_label_alt=True, **kwargs):
        self.show_label_alt = show_label_alt
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        if not self.show_label_alt:
            form.fields.pop('label_alt', None)
        else:
            form.fields['label'].widget = forms.Textarea(attrs={'rows': 1})
        return form

    @property
    def empty_form(self):
        form = super().empty_form
        if not self.show_label_alt:
            form.fields.pop('label_alt', None)
        else:
            form.fields['label'].widget = forms.Textarea(attrs={'rows': 1})
        return form


QuestionItemInlineFormset = inlineformset_factory(
    QuestionBase,
    QuestionItem,
    form=QuestionItemForm,
    formset=BaseQuestionItemFormset,
    extra=0
)


class ScalePointForm(forms.ModelForm):

    class Meta:
        model = ScalePoint
        fields = [
            'index',
            'value',
            'input_label',
            'heading_label',
            'secondary_point',
        ]

        labels = {
            'index': 'Position',
            'input_label': 'Label',
            'secondary_point': 'Extra option',
            'heading_label': 'Column heading',
        }

        help_texts = {
            # 'secondary_point': (
            #     'Not part of the main scale (e.g., "Don\'t know", '
            #     '"Prefer not to say")'
            # ),
        }


ScalePointInlineFormset = inlineformset_factory(
    QuestionBase,
    ScalePoint,
    form=ScalePointForm,
    extra=0
)


class FilterConditionForm(forms.ModelForm):
    source = forms.ChoiceField(
        choices=[],
        label='Compare to',
        required=True,
        widget=forms.Select(attrs={'class': 'w-100'})
    )
    condition_operator = forms.ChoiceField(
        choices=[],
        label='Operator',
        required=True,
        widget=forms.Select(attrs={'class': 'w-100'})
    )
    combinator = forms.ChoiceField(
        choices=[],
        label='Logic',
        required=True,
        widget=forms.Select(attrs={'class': 'w-100'})
    )
    condition_value = forms.CharField(
        label='Value',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    source_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    source_identifier = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = FilterCondition
        fields = [
            'index',
            'combinator',
            'source',
            'condition_operator',
            'condition_value',
            'source_type',
            'source_identifier'
        ]

    def __init__(self, *args, project=None, target_object=None, **kwargs):
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

    def _get_question_id(self):
        if isinstance(self.target_object, QuestionItem):
            return self.target_object.question.id
        else:
            return self.target_object.id

    def _setup_choices(self):
        """Configure all dropdown choices."""
        item_set = self._get_item_sources()
        question_set = self._get_question_sources()

        self.fields['source'].choices = [
            ('', 'Select variable...'),
            *self._build_source_choices(question_set, item_set)
        ]
        self.fields['condition_operator'].choices = [
            ('', 'Select operator...'),
            *FilterCondition.ConditionOperators.choices
        ]
        self.fields['combinator'].choices = [
            ('', 'Select logic...'),
            *FilterCondition.ConditionCombinators.choices
        ]

    def _set_initial_values(self):
        """Set initial form values for existing instances."""
        if not self.instance.pk:
            return

        source_id = (
                self.instance.source_question_id or
                self.instance.source_item_id or
                self.instance.source_identifier
        )
        self.initial['source'] = f'{self.instance.source_type}-{source_id}'

    # --- Source querysets ---

    def _get_item_sources(self):
        """Get QuestionItems available as filter sources.

        Exclude items that:
        -   are related to the same question as the target of the filter condition.
        -   are single choice items.
        """
        return (
            QuestionItem.objects
            .filter(question__project=self.project)
            .exclude(question__id=self.question_id)
            .exclude(question__question_type=QuestionType.SINGLE_CHOICE)
            .select_related('question')
        )

    def _get_question_sources(self):
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
            QuestionBase.objects
            .filter(project=self.project)
            .exclude(id=self.question_id)
            .exclude(question_type__in=excluded_types)
        )

        open_questions_with_items = (
            OpenQuestion.objects
            .filter(multi_item_response=True)
            .exclude(id=self.question_id)
            .values_list('id', flat=True)
        )
        return questions.exclude(id__in=open_questions_with_items)

    # --- Choice building ---

    def _build_source_choices(self, question_set, item_set):
        """Build and sort all source choices."""

        question_choices = [(FilterSourceTypes.QUESTION, q) for q in question_set]
        item_choices = [(FilterSourceTypes.QUESTION_ITEM, i) for i in item_set]
        combined = question_choices + item_choices

        # Sort by page and index
        combined = sorted(
            combined,
            key=lambda pair: (
                pair[1].page if hasattr(pair[1], 'page') else pair[1].question.page,
                pair[1].index
            )
        )

        # Add other variable types
        combined.extend(
            (FilterSourceTypes.URL_PARAMETER, v) for v in get_url_parameters(self.project)
        )
        combined.extend(
            (FilterSourceTypes.PARTICIPANT, v) for v in get_participant_variables()
        )
        combined.extend(
            (FilterSourceTypes.DONATION, v) for v in get_donation_variables()
        )

        return [self._create_source_label(src_type, obj) for src_type, obj in combined]

    def _create_source_label(self, source_type, obj):
        """Create a single (value, label) choice tuple."""
        CONFIG = {
            FilterSourceTypes.QUESTION: {
                'id': lambda o: o.id,
                'prefix': lambda o: f'[question, p{o.page}]',
                'label': lambda o: o.variable_name,
            },
            FilterSourceTypes.QUESTION_ITEM: {
                'id': lambda o: o.id,
                'prefix': lambda o: f'[item, p{o.question.page}]',
                'label': lambda o: f'{o.variable_name} ({o.label[:30] if o.label else None}{"..." if o.label and len(o.label or "") > 30 else ""})',
            },
            FilterSourceTypes.URL_PARAMETER: {
                'id': lambda o: o,
                'prefix': lambda o: '[url]',
                'label': lambda o: o,
            },
            FilterSourceTypes.PARTICIPANT: {
                'id': lambda o: o,
                'prefix': lambda o: '[participant]',
                'label': lambda o: o,
            },
            FilterSourceTypes.DONATION: {
                'id': lambda o: o,
                'prefix': lambda o: '[donation]',
                'label': lambda o: o,
            },
        }

        config = CONFIG.get(source_type)
        if not config:
            raise ValueError(f'Unknown source type: {source_type}')

        value = f'{source_type}-{config["id"](obj)}'
        label = f'{config["prefix"](obj)} {config["label"](obj)}'
        return (value, label)

    # --- Validation and saving ---

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')

        if not source:
            raise ValidationError('Please select a comparison variable.')

        try:
            source_type, source_id = source.split('-', 1)
        except ValueError:
            raise ValidationError('Invalid source format.')

        # Validate source exists
        self._validate_source(source_type, source_id)

        cleaned_data['source_type'] = source_type
        cleaned_data['source_identifier'] = source_id
        return cleaned_data

    def _validate_source(self, source_type, source_id):
        """Validate that the source object exists."""
        if source_type == FilterSourceTypes.QUESTION:
            if not QuestionBase.objects.filter(pk=source_id).exists():
                raise ValidationError('Selected question not found.')
        elif source_type == FilterSourceTypes.QUESTION_ITEM:
            if not QuestionItem.objects.filter(pk=source_id).exists():
                raise ValidationError('Selected item not found.')

    def save(self, commit=True):
        instance = super().save(commit=False)
        source_type, source_id = self.cleaned_data['source'].split('-', 1)

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
