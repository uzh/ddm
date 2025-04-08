from itertools import chain

from django import forms
from django.contrib.contenttypes.models import ContentType

from ddm.questionnaire.models import FilterCondition, QuestionBase, QuestionItem, QuestionType, OpenQuestion


class FilterConditionForm(forms.ModelForm):
    source = forms.ChoiceField(
        choices=[],
        label='Comparison Question/Item',
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

    class Meta:
        model = FilterCondition
        fields = [
            'index',
            'combinator',
            'source',
            'condition_operator',
            'condition_value'
        ]
        widgets = {
            'condition_value': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, project=None, target_object=None, **kwargs):
        """ Dynamically filter the object ID dropdowns based on ContentType selection. """
        super().__init__(*args, **kwargs)

        question_id = self.get_question_id(target_object)
        item_set = self.get_item_source_set(project, question_id)
        question_set = self.get_question_source_set(project, question_id)

        # Get choices for source field.
        self.fields['source'].choices = self.get_source_choices(question_set, item_set)

        # Get choices for other fields.
        self.fields['condition_operator'].choices = list(FilterCondition.ConditionOperators.choices)
        self.fields['combinator'].choices = list(FilterCondition.ConditionCombinators.choices)

        # Set initial values.
        if self.instance.pk and self.instance.source_object_id:
            prefix = 'item' if self.instance.source_content_type.model == 'questionitem' else 'question'
            self.initial['source'] = f'{prefix}-{self.instance.source_object_id}'

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

    def get_combined_labels(self, question_set, item_set):
        sorted_objects = sorted(
            chain(
                [(q, 'question') for q in question_set],
                [(i, 'item') for i in item_set]
            ),
            key=lambda pair: (
                pair[0].page if hasattr(pair[0], 'page') else pair[0].question.page,
                pair[0].index
            )
        )

        labels = []
        for obj in sorted_objects:
            if obj[1] == 'question':
                internal_id = f'question-{obj[0].id}'
                prefix = f'[quest, p{obj[0].page}]'
                var_name = obj[0].variable_name
                labels.append(
                    (f'{internal_id}', f'{prefix} {var_name}')
                )

            if obj[1] == 'item':
                internal_id = f'item-{obj[0].id}'
                prefix = f'[item, p{obj[0].question.page}]'
                label = f'{obj[0].variable_name} ({obj[0].label})'
                labels.append(
                    (f'{internal_id}', f'{prefix} {label}')
                )
        return labels

    def get_empty_form_defaults(self):
        self.fields['source'].choices.insert(0, (None, 'select comparison object'))
        self.fields['condition_operator'].choices.insert(0, (None, 'select condition operator'))
        self.fields['combinator'].choices.insert(0, (None, 'select combinator'))
        self.initial['condition_value'] = ''

    def get_source_choices(self, question_set, item_set):
        # Exclude nonsensical choices.
        item_ct = ContentType.objects.get_for_model(QuestionItem)

        if self.instance and self.instance.target_object_id:
            if self.instance.target_content_type == item_ct:
                # Exclude the item itself.
                item_set.exclude(id=self.instance.target_object_id)

                # Exclude the items belonging to the same question.
                item_set.exclude(question=self.instance.target.question)

                # Exclude the question to which the item belongs.
                question_set.exclude(id=self.instance.target.question.id)
            else:
                # Exclude the question.
                question_set.exclude(id=self.instance.target_object_id)

        # Add labels
        labels = self.get_combined_labels(question_set, item_set)
        return labels

    def clean(self):
        """
        Custom validation for condition operators based on source question type.
        """
        cleaned_data = super().clean()
        source_id = cleaned_data.get('source').split('-')
        if source_id[0] == 'item':
            source_object = QuestionItem.objects.get(id=source_id[1])
        else:
            source_object = QuestionBase.objects.get(id=source_id[1])
        cleaned_data['source_content_type'] = ContentType.objects.get_for_model(source_object)
        cleaned_data['source_object_id'] = source_object.pk

        # Ensure Index is unique per filter target.
        target_content_type = cleaned_data.get('target_content_type')
        target_object_id = cleaned_data.get('target_object_id')
        index = cleaned_data.get('index')
        if FilterCondition.objects.filter(
            target_content_type=target_content_type,
            target_object_id=target_object_id,
            index=index
        ).exists():
            raise forms.ValidationError('This index is already used for the selected target.')

        return cleaned_data


    def save(self, commit=True):
        """
        Ensure GenericForeignKey fields are properly saved.
        """
        instance = super().save(commit=False)

        if self.cleaned_data.get('source'):
            source_id = self.cleaned_data.get('source').split('-')

            if source_id[0] == 'item':
                source_object = QuestionItem.objects.get(id=source_id[1])
            else:
                source_object = QuestionBase.objects.get(id=source_id[1])

            if source_object:
                instance.source_content_type = ContentType.objects.get_for_model(source_object)
                instance.source_object_id = source_object.pk

        if commit:
            instance.save()
        return instance
