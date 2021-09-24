from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView

from ddm.admin_views import SurquestContextMixin, SurquestUpdateMixin
from ddm.forms import (
    OpenQuestionCreateForm, OpenQuestionUpdateForm,
    FileFeedbackCreateForm, FileFeedbackUpdateForm,
    FileUploadQuestionCreateForm, FileUploadQuestionUpdateForm,
    FileUploadInlineFormset,
    SingleChoiceQuestionCreateForm, SingleChoiceQuestionUpdateForm,
    QuestionItemInlineFormset, QuestionItemInlineListQFormset,
    QuestionItemInlineDiffQFormset, QuestionScaleInlineFormset
)
from ddm.models import (
    Questionnaire, Page,
    OpenQuestion, FileFeedback, FileUploadQuestion, MatrixQuestion,
    DifferentialQuestion, ListQuestion, TransitionQuestion,
    SingleChoiceQuestion, MultiChoiceQuestion
)


# Generic
# ----------------------------------------------------------------------
class QuestionBaseCreate(LoginRequiredMixin, SurquestContextMixin, CreateView):
    template_name = 'surquest/admin/questions/create.html'
    menu_levels = ['questionnaires', 'ind_questionnaire', 'page']
    url_para_page = 'p'
    view_name = None

    def __init__(self, *args, **kwargs):
        kwargs['view_name'] = self.model.DEFAULT_QUESTION_TYPE + '-create'
        super().__init__(*args, **kwargs)

    def get_initial(self):
        page_id = self.kwargs['p']
        page = Page.objects.get(pk=page_id)
        return {
            'page': page,
        }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['questionnaire'] = Questionnaire.objects.get(pk=self.kwargs['q'])
        context['page'] = Page.objects.get(pk=self.kwargs['p'])
        return context


class QuestionBaseUpdate(SurquestContextMixin, SurquestUpdateMixin, UpdateView):
    template_name = 'surquest/admin/questions/update.html'
    view_name = None

    def __init__(self, *args, **kwargs):
        kwargs['view_name'] = self.model.DEFAULT_QUESTION_TYPE + '-update'
        super().__init__(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        instance = self.object
        context['questionnaire'] = instance.page.questionnaire
        context['page'] = instance.page
        context['question'] = instance
        context['show_filter_link'] = True
        return context

    def get_success_url(self):
        return reverse(self.view_name,
                       kwargs={'pk': self.object.pk,
                               'q': self.object.page.questionnaire.pk})


# Open Question
# ----------------------------------------------------------------------
class OpenQuestionCreate(QuestionBaseCreate):
    model = OpenQuestion
    form_class = OpenQuestionCreateForm


class OpenQuestionUpdate(QuestionBaseUpdate):
    model = OpenQuestion
    form_class = OpenQuestionUpdateForm

    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': [
                'name', 'variable_name', 'question_text', 'question_instruction'
            ]
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        },
        {
            'name': 'Advanced Options',
            'description': 'Description for advanced options',
            'type': 'basic_form',
            'fields': [
                'required', 'encrypt', 'input_format', 'display_size',
                'max_input_length'
            ]
        }
    ]


# Transition Question
# ----------------------------------------------------------------------
class TransitionQuestionCreate(QuestionBaseCreate):
    model = TransitionQuestion
    fields = ['page', 'name']


class TransitionQuestionUpdate(QuestionBaseUpdate):
    model = TransitionQuestion
    fields = [
        'page',
        'name',
        'question_text',
        'question_instruction',
        'index'
    ]
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': ['name', 'question_text', 'question_instruction']
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        }
    ]


# Single Choice Question
# ----------------------------------------------------------------------
class SingleChoiceQuestionCreate(QuestionBaseCreate):
    model = SingleChoiceQuestion
    form_class = SingleChoiceQuestionCreateForm


class SingleChoiceQuestionUpdate(QuestionBaseUpdate):
    model = SingleChoiceQuestion
    form_class = SingleChoiceQuestionUpdateForm

    inline_formsets = [
        {'label': 'Question Items', 'formset': QuestionItemInlineFormset}
    ]
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': [
                'name', 'variable_name', 'question_text', 'question_instruction'
            ]
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        },
        {
            'name': 'Advanced Options',
            'description': 'Description for advanced options',
            'type': 'basic_form',
            'fields': ['required']
        }
    ]


# Multi Choice Question
# ----------------------------------------------------------------------
class MultiChoiceQuestionCreate(QuestionBaseCreate):
    model = MultiChoiceQuestion
    fields = ['page', 'name']


class MultiChoiceQuestionUpdate(QuestionBaseUpdate):
    model = MultiChoiceQuestion
    fields = [
        'page',
        'name',
        'question_text',
        'question_instruction',
        'required',
        'index'
    ]
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': ['name', 'question_text', 'question_instruction']
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        },
        {
            'name': 'Advanced Options',
            'description': 'Description for advanced options',
            'type': 'basic_form',
            'fields': ['required']
        },
        {
            'name': 'Question Items',
            'description': 'Description for Question Items',
            'type': 'inline_form',
            'formset_class': QuestionItemInlineFormset
        }
    ]


# List Question
# ----------------------------------------------------------------------
class ListQuestionCreate(QuestionBaseCreate):
    model = ListQuestion
    fields = ['page', 'name']


class ListQuestionUpdate(QuestionBaseUpdate):
    model = ListQuestion
    fields = [
        'page', 'name', 'question_text', 'question_instruction',
        'index', 'required', 'encrypt'
    ]
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': ['name', 'question_text', 'question_instruction']
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        },
        {
            'name': 'Advanced Options',
            'description': 'Description for advanced options',
            'type': 'basic_form',
            'fields': ['required', 'encrypt']
        },
        {
            'name': 'Question Items',
            'description': 'Description for Question Items',
            'type': 'inline_form',
            'formset_class': QuestionItemInlineListQFormset
        }
    ]


# Matrix Question
# ----------------------------------------------------------------------
class MatrixQuestionCreate(QuestionBaseCreate):
    model = MatrixQuestion
    fields = ['page', 'name']


class MatrixQuestionUpdate(QuestionBaseUpdate):
    model = MatrixQuestion
    menu_levels = ['questionnaires', 'ind_questionnaire']
    fields = [
        'page',
        'name',
        'question_text',
        'question_instruction',
        'required',
        'index',
        'scale_repetition'
    ]
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': ['name', 'question_text', 'question_instruction']
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        },
        {
            'name': 'Advanced Options',
            'description': 'Description for advanced options',
            'type': 'basic_form',
            'fields': ['required', 'scale_repetition']
        },
        {
            'name': 'Question Scale',
            'description': 'Description of Question Scale',
            'type': 'inline_form',
            'formset_class': QuestionScaleInlineFormset
        },
        {
            'name': 'Question Items',
            'description': 'Description of Question Items',
            'type': 'inline_form',
            'formset_class': QuestionItemInlineFormset
        },
    ]


# Differential Question
# ----------------------------------------------------------------------
class DifferentialQuestionCreate(QuestionBaseCreate):
    model = DifferentialQuestion
    fields = ['page', 'name']


class DifferentialQuestionUpdate(QuestionBaseUpdate):
    model = DifferentialQuestion
    fields = [
        'page',
        'name',
        'question_text',
        'question_instruction',
        'required',
        'scale_points',
        'index'
    ]
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': ['name', 'question_text', 'question_instruction']
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        },
        {
            'name': 'Advanced Options',
            'description': 'Description for advanced options',
            'type': 'basic_form',
            'fields': ['required', 'scale_points']
        },
        {
            'name': 'Question Items',
            'description': 'Description for Question Items',
            'type': 'inline_form',
            'formset_class': QuestionItemInlineDiffQFormset
        }
    ]


# File Upload Question
# ----------------------------------------------------------------------
class FileUploadQuestionCreate(QuestionBaseCreate):
    model = FileUploadQuestion
    form_class = FileUploadQuestionCreateForm


class FileUploadQuestionUpdate(QuestionBaseUpdate):
    model = FileUploadQuestion
    form_class = FileUploadQuestionUpdateForm
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': [
                'name', 'variable_name', 'question_text', 'question_instruction'
            ]
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        },
        {
            'name': 'Advanced Options',
            'description': 'Description for advanced options',
            'type': 'basic_form',
            'fields': ['required', 'upload_mode', 'max_filesize']
        },
        {
            'name': 'File Uploads',
            'description': 'Description for File Uploads',
            'type': 'inline_form',
            'formset_class': FileUploadInlineFormset
        }
    ]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['show_filter_link'] = False
        return context


# File Feedback Question
# ----------------------------------------------------------------------
class FileFeedbackCreate(QuestionBaseCreate):
    model = FileFeedback
    form_class = FileFeedbackCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        page = Page.objects.filter(id=self.kwargs['p']).first()
        kwargs['qstnr_id'] = page.questionnaire.pk
        return kwargs


class FileFeedbackUpdate(QuestionBaseUpdate):
    model = FileFeedback
    form_class = FileFeedbackUpdateForm
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': [
                'name', 'variable_name', 'question_text', 'question_instruction'
            ]
        },
        {
            'name': 'Positioning',
            'description': 'Description for positioning',
            'type': 'basic_form',
            'fields': ['page', 'index']
        },
        {
            'name': 'Advanced Options',
            'description': 'Description for advanced options',
            'type': 'basic_form',
            'fields': [
                'required', 'related_filequestion', 'need_to_confirm',
                'display_upload_stats', 'display_upload_table'
            ]
        }
    ]
