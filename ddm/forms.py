from django import forms
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError

from ddm import models


# ----------------------------------------------------------------------
# GENERAL
# ----------------------------------------------------------------------
class VariableNameValidationForm(forms.ModelForm):
    def clean(self):
        """
        Validate that variable_name is unique for one questionnaire.
        """
        cleaned_data = super().clean()
        var_name = cleaned_data.get('variable_name')

        # For triggers retrieve the questionnaire instance as follows:
        questionnaire = cleaned_data.get('questionnaire')
        # For pages retrieve the questionnaire instance as follows:
        if questionnaire is None:
            page = cleaned_data.get('page')
            questionnaire = page.questionnaire

        if self.instance.pk is not None:
            self_id = self.instance.pk

            if hasattr(self.instance, 'question_type'):
                var_names = questionnaire.get_var_names(
                    excluded_questions=[self_id]
                )
            elif hasattr(self.instance, 'trigger_type'):
                var_names = questionnaire.get_var_names(
                    excluded_triggers=[self_id]
                )
            elif isinstance(self.instance, models.ExternalVariable):
                var_names = questionnaire.get_var_names(
                    excluded_externals=[self_id]
                )

        else:
            var_names = questionnaire.get_var_names()

        if var_name in var_names:
            error_message = (
                'Variable Name already exists but must be unique. Please '
                'choose another variable name.'
            )
            self.add_error('variable_name', error_message)
            # TODO: Check the following commented line of code:
            # raise forms.ValidationError({'variable_name': error_message})

        return cleaned_data


class VarFromDataVarnameValidation(forms.ModelForm):
    """
    Validate that variable name is unique when creating variables through
    a 'Variables from Data' Trigger
    """
    def clean(self):
        cleaned_data = super().clean()
        var_name_stem = cleaned_data.get('variable_name_stem')
        n_variables = cleaned_data.get('n_variables')
        var_names = []
        for i in range(1, n_variables+1):
            var_names.append(var_name_stem + '_' + str(i))

        # Get all variable names associated with the questionnaire.
        questionnaire = cleaned_data.get('questionnaire')
        if self.instance.pk is not None:
            self_id = self.instance.pk
            existing_var_names = questionnaire.get_var_names(
                excluded_triggers=[self_id])
        else:
            existing_var_names = questionnaire.get_var_names()

        if any(item in var_names for item in existing_var_names):
            error_message = (
                'Variables with this variable stem already exist. Please '
                'choose another variable name stem for this trigger.'
            )
            raise ValidationError({'variable_name_stem': error_message})


class ItemVarnameValidation(forms.BaseInlineFormSet):
    def clean(self):
        """
        Validate that variable_name is unique for question items related
        to one questionnaire.
        """
        super().clean()

        if len(self.forms) > 0:
            variable_names_form = []
            initial_var_names = []
            new_var_names = []

            # Check if a variable name appears multiple times in the formset.
            for form in self.forms:
                var_name = form.cleaned_data.get('variable_name', None)
                if var_name is not None:
                    variable_names_form.append(var_name)

                    if 'variable_name' in form.changed_data:
                        if hasattr(form.instance, 'variable'):
                            if form.instance.variable is not None:
                                initial_var_names.append(form.instance.variable.name)

                        new_var_names.append(var_name)

            if len(variable_names_form) > len(set(variable_names_form)):
                error_message = (
                    'There is another question item with the same variable '
                    'name. Please change this variable name, as variable '
                    'names must be unique.'
                )
                form.add_error('variable_name', error_message)

            var_name_intersection = set(initial_var_names).intersection(set(new_var_names))

            if len(var_name_intersection) > 0:
                for var_name in var_name_intersection:
                    index_initial_var_names = initial_var_names.index(var_name)
                    index_new_var_names = new_var_names.index(var_name)
                    if index_initial_var_names > index_new_var_names:
                        error_message = (
                            'There is another question item with the same variable '
                            'name in the database. If you are trying to '
                            'exchange the variable names of two items, '
                            'try to do it in two steps.'
                        )
                        form.add_error('variable_name', error_message)

            # Get the related question and questionnaire.
            question = self.instance
            question_id = question.pk
            questionnaire = question.page.questionnaire

            # Get all variable names, excluding those associated with the question.
            var_names_questionnaire = questionnaire.get_var_names(
                excluded_questions=[question_id])

            for form in self.forms:
                if 'variable_name' in form.cleaned_data:
                    variable_name = form.cleaned_data['variable_name']
                else:
                    variable_name = None

                if variable_name in var_names_questionnaire:
                    error_message = (
                        'There is already another question item with '
                        f'"{variable_name}" as variable name. Variable names '
                        'must be unique within one questionnaire. Please '
                        'choose another variable name.'
                    )
                    form.add_error('variable_name', error_message)


# ----------------------------------------------------------------------
# QUESTIONNAIRE
# ----------------------------------------------------------------------
class QuestionnaireStructureForm(forms.ModelForm):
    class Meta:
        model = models.Questionnaire
        fields = ['name']
        widgets = {'name': forms.HiddenInput()}


# ----------------------------------------------------------------------
# PAGES
# ----------------------------------------------------------------------
class PageInlineForm(forms.ModelForm):
    class Meta:
        model = models.Page
        fields = ['name', 'page_type', 'index']
        widgets = {
            'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'page_type': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


PageInlineFormSet = inlineformset_factory(
    models.Questionnaire,
    models.Page,
    form=PageInlineForm,
    extra=0
)


class QuestionPageForm(forms.ModelForm):
    class Meta:
        model = models.QuestionPage
        fields = [
            'questionnaire',
            'name',
            'show_back_button'
        ]
        widgets = {'questionnaire': forms.HiddenInput()}


class EndPageForm(forms.ModelForm):
    class Meta:
        model = models.EndPage
        fields = [
            'questionnaire',
            'name',
            'redirect',
            'redirect_url',
            'show_back_button'
        ]
        widgets = {'questionnaire': forms.HiddenInput()}


# ----------------------------------------------------------------------
# QUESTIONS
# ----------------------------------------------------------------------

# General
# ----------------------------------------------------------------------
class QuestionInlineForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['page', 'name', 'question_type', 'index']
        widgets = {
            'page': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'question_type': forms.TextInput(attrs={'readonly': 'readonly'})
        }


QuestionInlineFormset = inlineformset_factory(
    models.Page,
    models.Question,
    form=QuestionInlineForm,
    extra=0
)


# Open Question
# ----------------------------------------------------------------------
class OpenQuestionCreateForm(VariableNameValidationForm):
    class Meta:
        model = models.OpenQuestion
        fields = ['page', 'name', 'variable_name']


class OpenQuestionUpdateForm(VariableNameValidationForm):
    class Meta:
        model = models.OpenQuestion
        fields = [
            'page',
            'name',
            'question_text',
            'question_instruction',
            'variable_name',
            'required',
            'encrypt',
            'input_format',
            'display_size',
            'max_input_length',
            'index'
        ]


# Single Choice Question
# ----------------------------------------------------------------------
class SingleChoiceQuestionCreateForm(VariableNameValidationForm):
    class Meta:
        model = models.SingleChoiceQuestion
        fields = ['page', 'name', 'variable_name']


class SingleChoiceQuestionUpdateForm(VariableNameValidationForm):
    class Meta:
        model = models.SingleChoiceQuestion
        fields = [
            'page',
            'name',
            'question_text',
            'question_instruction',
            'variable_name',
            'required',
            'index'
        ]


# File Upload
# ----------------------------------------------------------------------
class FileUploadQuestionCreateForm(VariableNameValidationForm):
    class Meta:
        model = models.FileUploadQuestion
        fields = ['page', 'name', 'variable_name']


class FileUploadQuestionUpdateForm(VariableNameValidationForm):
    class Meta:
        model = models.FileUploadQuestion
        fields = [
            'page',
            'name',
            'question_text',
            'question_instruction',
            'variable_name',
            'required',
            'requires_consent',
            'max_filesize',
            'index',
            'upload_mode'
        ]


class FileUploadItemsInlineForm(forms.ModelForm):
    class Meta:
        model = models.FileUploadItem
        fields = [
            'file_upload_question',
            'variable_name',
            'valid_file_types',
            'max_filesize',
            'expected_filename',
            'validation_fields',
            'extraction_fields'
        ]
        widgets = {
            'file_upload_question': forms.HiddenInput(),
            'validation_fields': forms.TextInput(
                attrs={'style': 'width: 250px !important;'}
            ),
            'extraction_fields': forms.TextInput(
                attrs={'style': 'width: 250px !important;'}
            )
        }


FileUploadInlineFormset = inlineformset_factory(
    models.FileUploadQuestion,
    models.FileUploadItem,
    form=FileUploadItemsInlineForm,
    formset=ItemVarnameValidation,
    extra=1
)


# File Feedback Question
# ----------------------------------------------------------------------
class CustomFileUploadChoice(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.variable_name}'


class FileFeedbackCreateForm(VariableNameValidationForm):
    related_filequestion = CustomFileUploadChoice(queryset=None)

    class Meta:
        model = models.FileFeedback
        fields = ['page', 'name', 'related_filequestion', 'variable_name']

    def __init__(self, *args, **kwargs):
        self.qstnr_id = kwargs.pop('qstnr_id', None)
        super().__init__(*args, **kwargs)
        if self.qstnr_id is not None:
            qs = models.FileUploadItem.objects.filter(
                file_upload_question__page__questionnaire__pk=self.qstnr_id
            )
        else:
            qs = models.FileUploadItem.objects.all()

        self.fields['related_filequestion'].queryset = qs


class FileFeedbackUpdateForm(VariableNameValidationForm):
    related_filequestion = CustomFileUploadChoice(queryset=None)

    class Meta:
        model = models.FileFeedback
        fields = [
            'page',
            'name',
            'question_text',
            'question_instruction',
            'variable_name',
            'required',
            'index',
            'related_filequestion',
            'need_to_confirm',
            'display_upload_table',
            'display_upload_stats'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            qs = models.FileUploadItem.objects.filter(
                file_upload_question__page__questionnaire__pk=self.instance.page.questionnaire.pk
            )
        else:
            qs = models.FileUploadItem.objects.all()

        self.fields['related_filequestion'].queryset = qs


# ----------------------------------------------------------------------
# QUESTION ITEMS
# ----------------------------------------------------------------------

# General
# ----------------------------------------------------------------------
class QuestionItemInlineForm(forms.ModelForm):
    class Meta:
        model = models.QuestionItem
        fields = [
            'question',
            'answer',
            'variable_name',
            'index',
            'value',
            'randomize'
        ]
        widgets = {
            'question': forms.HiddenInput()
        }


class QuestionItemInlineDiffQForm(forms.ModelForm):
    class Meta:
        model = models.QuestionItem
        fields = [
            'question',
            'answer',
            'answer_alt',
            'variable_name',
            'index',
            'value',
            'randomize'
        ]
        widgets = {
            'question': forms.HiddenInput()
        }


class QuestionItemInlineListQForm(forms.ModelForm):
    class Meta:
        model = models.QuestionItem
        fields = [
            'question',
            'answer',
            'variable_name',
            'index',
            'value'
        ]
        widgets = {
            'question': forms.HiddenInput()
        }


QuestionItemInlineFormset = inlineformset_factory(
    models.Question,
    models.QuestionItem,
    form=QuestionItemInlineForm,
    formset=ItemVarnameValidation,
    extra=1
)


QuestionItemInlineDiffQFormset = inlineformset_factory(
    models.Question,
    models.QuestionItem,
    form=QuestionItemInlineDiffQForm,
    formset=ItemVarnameValidation,
    extra=1
)


QuestionItemInlineListQFormset = inlineformset_factory(
    models.Question,
    models.QuestionItem,
    form=QuestionItemInlineListQForm,
    formset=ItemVarnameValidation,
    extra=1
)


# ----------------------------------------------------------------------
# QUESTION SCALE
# ----------------------------------------------------------------------
class QuestionScaleInlineForm(forms.ModelForm):
    class Meta:
        model = models.QuestionScale
        fields = ['label', 'value', 'index', 'add_border']


QuestionScaleInlineFormset = inlineformset_factory(
    models.MatrixQuestion,
    models.QuestionScale,
    form=QuestionScaleInlineForm,
    extra=1
)


# ----------------------------------------------------------------------
# TRIGGER
# ----------------------------------------------------------------------
class TriggerInlineForm(forms.ModelForm):
    class Meta:
        model = models.Trigger
        fields = ['name', 'trigger_type', 'execution_page', 'execution_point']
        widgets = {
            'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'trigger_type': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


TriggerInlineFormSet = inlineformset_factory(
    models.Questionnaire,
    models.Trigger,
    form=TriggerInlineForm,
    extra=0
)


class TokenGeneratorForm(forms.ModelForm):
    class Meta:
        model = models.TokenGenerator
        fields = [
            'questionnaire',
            'name',
            'target',
            'store_in_response',
            'variable_name',
            'included_vars',
            'execution_page',
            'execution_point',
            'include_session_id'
        ]
        widgets = {'questionnaire': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        self.qstnr_id = kwargs.pop('qstnr_id', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk is not None:
            qs = models.Page.objects.filter(
                questionnaire=self.instance.questionnaire
            )
        else:
            qs = models.Page.objects.filter(
                questionnaire__pk=self.qstnr_id
            )

        self.fields['execution_page'].queryset = qs


class VariablesFromDataForm(VarFromDataVarnameValidation):
    related_upload_question = CustomFileUploadChoice(queryset=None)

    class Meta:
        model = models.VariablesFromData
        fields = [
            'questionnaire',
            'name',
            'related_upload_question',
            'execution_page',
            'execution_point',
            'variable_name_stem',
            'n_variables',
            'field_to_extract',
            'filter_active',
            'filter_condition'
        ]
        widgets = {'questionnaire': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        self.qstnr_id = kwargs.pop('qstnr_id', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk is not None:
            qs_ulq = models.FileUploadItem.objects.filter(
                file_upload_question__page__questionnaire=self.instance.questionnaire
            )
            qs_page = models.Page.objects.filter(
                questionnaire=self.instance.questionnaire
            )
        else:
            qs_ulq = models.FileUploadItem.objects.filter(
                file_upload_question__page__questionnaire__pk=self.qstnr_id
            )
            qs_page = models.Page.objects.filter(
                questionnaire__pk=self.qstnr_id
            )

        self.fields['related_upload_question'].queryset = qs_ulq
        self.fields['execution_page'].queryset = qs_page


class EmailTriggerForm(forms.ModelForm):
    class Meta:
        model = models.EmailTrigger
        fields = [
            'questionnaire',
            'name',
            'execution_page',
            'execution_point',
            'from_email',
            'to_email',
            'subject',
            'message',
            'execution_time',
            'execution_delay'
        ]
        widgets = {'questionnaire': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        self.qstnr_id = kwargs.pop('qstnr_id', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk is not None:
            qs = models.Page.objects.filter(questionnaire=self.instance.questionnaire)
        else:
            qs = models.Page.objects.filter(questionnaire__pk=self.qstnr_id)

        self.fields['execution_page'].queryset = qs


class CleanUploadTriggerForm(forms.ModelForm):
    class Meta:
        model = models.CleanUploadDataTrigger
        fields = [
            'questionnaire',
            'name',
            'execution_page',
            'execution_point',
        ]
        widgets = {'questionnaire': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        self.qstnr_id = kwargs.pop('qstnr_id', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk is not None:
            qs = models.Page.objects.filter(questionnaire=self.instance.questionnaire)
        else:
            qs = models.Page.objects.filter(questionnaire__pk=self.qstnr_id)

        self.fields['execution_page'].queryset = qs


# ----------------------------------------------------------------------
# EXTERNAL VARIABLE
# ----------------------------------------------------------------------
class ExternalVariableInlineForm(forms.ModelForm):
    class Meta:
        model = models.ExternalVariable
        fields = ['variable_name', 'source', 'related_parameter']


class ExternalVariableFormset(forms.BaseInlineFormSet):
    def clean(self):
        """
        Checks variable names of external variables.
        """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own.
            return
        ext_var_names = []

        questionnaire = None
        ext_var_pks = []

        # Check that each external variable has a unique variable name.
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue

            if questionnaire is None:
                questionnaire = form.cleaned_data.get('questionnaire')

            ext_var_pks.append(form.instance.pk)

            name = form.cleaned_data.get('variable_name')
            if name in ext_var_names:
                error_message = (
                    'Form could not be saved. Variable names of external '
                    'variables must be unique.'
                )
                form.add_error('variable_name', error_message)
            ext_var_names.append(name)

        # Compare the names of external variables to the variable names of other
        # objects.
        var_names = questionnaire.get_var_names(excluded_externals=ext_var_pks)

        if any(item in ext_var_names for item in var_names):
            error_message = (
                'Variables with this variable stem already exist. Please '
                'choose another variable name stem for this trigger.'
            )
            raise ValidationError(error_message)


external_variable_formset = inlineformset_factory(
    models.Questionnaire,
    models.ExternalVariable,
    form=ExternalVariableInlineForm,
    formset=ExternalVariableFormset,
    extra=1
)


# ----------------------------------------------------------------------
# FILTERS
# ----------------------------------------------------------------------
class FilterForm(forms.ModelForm):
    filter_variable_name = forms.ChoiceField(choices=[])

    class Meta:
        model = models.FilterCondition
        fields = ['name', 'filter_variable_name',
                  'comparison_type', 'comparison_value',
                  'target_question', 'target_question_item']
        widgets = {'target_question': forms.HiddenInput(),
                   'target_question_item': forms.HiddenInput()}

    def __init__(self, target_question=None, target_question_item=None,
                 variable_choices=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['filter_variable_name'].choices = variable_choices
        self.fields['target_question'].initial = target_question
        self.fields['target_question_item'].initial = target_question_item

    def clean(self):
        super().clean()


class FilterFormset(forms.BaseModelFormSet):
    def clean(self):
        """
        Checks that no two filters have the same name.
        """
        if any(self.errors):
            # Don't validate the formset unless each form is valid on its own.
            return
        filter_names = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            name = form.cleaned_data.get('name')
            if name in filter_names:
                raise ValidationError(
                    'Form could not be saved. Filters belonging to the same '
                    'question/question item must have unique names.'
                )
            filter_names.append(name)


class FilterSequenceForm(forms.ModelForm):
    class Meta:
        model = models.FilterSequence
        fields = ['logic', 'sequence']
