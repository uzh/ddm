from itertools import chain

from django import forms
from django.core.exceptions import ValidationError

from ddm.projects.service import (
    get_url_parameters, get_participant_variables, get_donation_variables
)
from ddm.questionnaire.models import (
    FilterCondition, QuestionBase, QuestionItem, QuestionType, OpenQuestion,
    FilterSourceTypes
)


class FilterConditionForm(forms.ModelForm):
    source = forms.ChoiceField(
        choices=[],
        label='Comparison Variable',
        required=True,
        widget=forms.Select(attrs={'class': 'w-100'})
    )
    condition_operator = forms.ChoiceField(
        choices=[],
        label='Comparison Operator',
        required=True,
        widget=forms.Select(attrs={'class': 'w-100'})
    )
    combinator = forms.ChoiceField(
        choices=[],
        label='Combinator',
        required=True,
        widget=forms.Select(attrs={'class': 'w-100'})
    )
    condition_value = forms.CharField(
        label='Comparison Value',
        required=True
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
        widgets = {
            'condition_value': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, project=None, target_object=None, **kwargs):
        """
        Dynamically filter the object ID dropdowns based on ContentType selection.
        """
        super().__init__(*args, **kwargs)

        question_id = self.get_question_id(target_object)
        item_set = self.get_item_source_set(project, question_id)
        question_set = self.get_question_source_set(project, question_id)

        # Get choices for source field.
        self.fields['source'].choices = self.get_source_choices(question_set, item_set, project)

        # Get choices for other fields.
        self.fields['condition_operator'].choices = list(FilterCondition.ConditionOperators.choices)
        self.fields['combinator'].choices = list(FilterCondition.ConditionCombinators.choices)

        # Add default choices for empty formsets.
        self.fields['source'].choices.insert(0, (None, 'select comparison object'))
        self.fields['condition_operator'].choices.insert(0, (None, 'select condition operator'))
        self.fields['combinator'].choices.insert(0, (None, 'select combinator'))

        # Set initial values.
        if self.instance.pk:
            if self.instance.source_question:
                source_id = self.instance.source_question.pk
            elif self.instance.source_item:
                source_id = self.instance.source_item.pk
            else:
                source_id = self.instance.source_identifier

            self.initial['source'] = f'{self.instance.source_type}-{source_id}'

        else:
            self.get_empty_form_defaults()

    def get_question_id(self, target_object):
        if isinstance(target_object, QuestionItem):
            return target_object.question.id
        else:
            return target_object.id

    def get_item_source_set(self, project, question_id):
        """
        Get the set of QuestionItems that should be included in the choices
        for the source field.
        Exclude items that:
        -   are related to the same question as the target of the filter condition.
        -   are single choice items.
        """
        item_set = (
            QuestionItem.objects
            .filter(question__project=project)
            .exclude(question__id=question_id)
            .exclude(question__question_type=QuestionType.SINGLE_CHOICE)
        )
        return item_set

    def get_question_source_set(self, project, question_id):
        """
        Get the set of questions that should be included in the choices
        for the source field.
        Exclude questions:
        -   where the response is recorded in relation to the items.
        """
        types_to_exclude = [
            QuestionType.GENERIC,
            QuestionType.TRANSITION,
            QuestionType.MULTI_CHOICE,
            QuestionType.MATRIX,
            QuestionType.SEMANTIC_DIFF,
        ]
        question_set = (
            QuestionBase.objects
            .filter(project=project)
            .exclude(id=question_id)
            .exclude(question_type__in=types_to_exclude)
        )

        open_questions_with_items = (
            OpenQuestion.objects
            .filter(multi_item_response=True)
            .exclude(id=question_id)
        )
        for question in open_questions_with_items:
            question_set = question_set.exclude(id=question.id)
        return question_set

    def sort_questions_and_items(self, question_and_item_set):
        sorted_objects = sorted(
            question_and_item_set,
            key=lambda pair: (
                pair[1].page if hasattr(pair[1], 'page') else pair[1].question.page,
                pair[1].index
            )
        )
        return sorted_objects

    def create_source_label(self, source_type, details):
        """
        Create the labels displayed in the form's source select dropdown.
        """
        if source_type == FilterSourceTypes.QUESTION:
            internal_id = f'{source_type}-{details.id}'
            prefix = f'[question, p{details.page}]'
            descr = details.variable_name

        elif source_type == FilterSourceTypes.QUESTION_ITEM:
            internal_id = f'{source_type}-{details.id}'
            prefix = f'[item, p{details.question.page}]'
            if details.label and len(details.label) > 30:
                descr_detail = details.label[:30] + '...'
            else:
                descr_detail = details.label[:30]
            descr = f'{details.variable_name} ({descr_detail})'

        elif source_type == FilterSourceTypes.URL_PARAMETER:
            internal_id = f'{source_type}-{details}'
            prefix = '[url]'
            descr = details

        elif source_type == FilterSourceTypes.SYSTEM:
            internal_id = f'{source_type}-{details}'
            prefix = '[system]'
            descr = details

        elif source_type == FilterSourceTypes.PARTICIPANT:
            internal_id = f'{source_type}-{details}'
            prefix = '[participant]'
            descr = details

        elif source_type == FilterSourceTypes.DONATION:
            internal_id = f'{source_type}-{details}'
            prefix = '[donation]'
            descr = details

        else:
            raise ValueError(f'Unknown source type: {source_type}')

        return (internal_id, f'{prefix} {descr}')

    def get_empty_form_defaults(self):
        self.initial['condition_value'] = ''

    def get_source_choices(self, question_set, item_set, project):
        """
        Get the source choices.
        """
        # Add questionnaire variables.
        if self.instance.target_question:
            question_set.exclude(pk=self.instance.target_question.pk)

        elif self.instance.target_item:
            question = self.instance.target_item.question
            question_set.exclude(pk=question.pk)
            item_set.exclude(question=question)

        combined_set = chain(
            [(FilterSourceTypes.QUESTION, q) for q in question_set],
            [(FilterSourceTypes.QUESTION_ITEM, i) for i in item_set]
        )
        sorted_choices = self.sort_questions_and_items(combined_set)

        # Add url_parameter variables.
        for var in get_url_parameters(project):
            sorted_choices.append((FilterSourceTypes.URL_PARAMETER, var))

        # Add participant variables.
        for var in get_participant_variables():
            sorted_choices.append((FilterSourceTypes.PARTICIPANT, var))

        # Add donation variables.
        for var in get_donation_variables():
            sorted_choices.append((FilterSourceTypes.DONATION, var))

        # Add labels
        labels = []
        for choice in sorted_choices:
            labels.append(self.create_source_label(choice[0], choice[1]))

        return labels

    def clean(self):
        """
        Custom validation for condition operators based on source type.
        """
        cleaned_data = super().clean()

        # Check that source is set.
        source = self.cleaned_data.get('source')
        if source is None or source == '':
            raise ValidationError('A source must be selected.')

        # Check that source has the correct format.
        source_parts = source.split('-')
        if len(source_parts) != 2:
            raise ValidationError('Invalid source format')

        source_type = source_parts[0]
        source_id = source_parts[1]

        if source_type == FilterSourceTypes.QUESTION:
            try:
                QuestionBase.objects.get(pk=source_id)
                cleaned_data['source_type'] = source_type
                cleaned_data['source_identifier'] = source_id
            except QuestionBase.DoesNotExist:
                raise ValidationError('Invalid question ID')

        elif source_type == FilterSourceTypes.QUESTION_ITEM:
            try:
                QuestionItem.objects.get(pk=source_id)
                cleaned_data['source_type'] = source_type
                cleaned_data['source_identifier'] = source_id
            except QuestionItem.DoesNotExist:
                raise ValidationError('Invalid ID for source item')

        else:
            cleaned_data['source_type'] = source_type
            cleaned_data['source_identifier'] = source_id
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Get source type and source ID.
        source = self.cleaned_data.get('source')
        source = source.split('-')
        source_type = source[0]
        source_id = source[1]

        if source_type == FilterSourceTypes.QUESTION:
            instance.source_question = QuestionBase.objects.get(pk=source_id)
            instance.source_item = None
            instance.source_identifier = None

        elif source_type == FilterSourceTypes.QUESTION_ITEM:
            instance.source_item = QuestionItem.objects.get(pk=source_id)
            instance.source_question = None
            instance.source_identifier = None

        else:
            instance.source_identifier = source_id
            instance.source_question = None
            instance.source_item = None

        instance.source_type = source_type

        if commit:
            instance.save()
        return instance
