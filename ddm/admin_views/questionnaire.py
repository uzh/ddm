from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from ddm.models import Questionnaire, Page, FileUploadQuestion, Trigger
from ddm.forms import (
    QuestionnaireStructureForm, PageInlineFormSet, external_variable_formset,
    TriggerInlineFormSet
)
from ddm.admin_views import SurquestContextMixin, SurquestUpdateMixin


class QuestionnaireList(LoginRequiredMixin, SurquestContextMixin, ListView):
    """View to display list of available questionnaires.
    """

    model = Questionnaire
    template_name = 'ddm/admin/questionnaires/questionnaire_list.html'


class QuestionnaireCreate(LoginRequiredMixin, SurquestContextMixin, CreateView):
    """View to create a questionnaire
    """

    model = Questionnaire
    fields = ['name', 'description', 'slug']
    template_name = 'ddm/admin/questionnaires/create.html'


class QuestionnaireDelete(LoginRequiredMixin, SurquestContextMixin, DeleteView):
    """View to delete existing questionnaire.
    """

    model = Questionnaire
    success_url = reverse_lazy('questionnaire-list')
    template_name = 'ddm/admin/questionnaires/delete.html'
    view_name = 'questionnaire-delete'


class QuestionnaireBaseUpdate(LoginRequiredMixin, SurquestUpdateMixin,
                              UpdateView):
    """View template for other questionnaire related views to inherit from.
    """

    model = Questionnaire
    view_name = None


class QuestionnaireGeneralSettingsUpdate(SurquestContextMixin,
                                         SurquestUpdateMixin, UpdateView):
    """View to display general questionnaire settings.
    """

    model = Questionnaire
    template_name = 'ddm/admin/questionnaires/general_settings.html'
    view_name = 'questionnaire-settings'

    fields = [
        'name',
        'description',
        'slug',
        'accessibility',
        'active',
        'missing_not_answered',
        'missing_not_seen',
        'missing_invalid',
        'enable_continuation'
    ]
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': ['name', 'description']
        },
        {
            'name': 'Accessibility',
            'description': 'Description for Accessibility',
            'type': 'basic_form',
            'fields': ['slug', 'active', 'accessibility', 'enable_continuation']
        },
        {
            'name': 'Variable Definitions',
            'description': 'Description for Variable Definition',
            'type': 'basic_form',
            'fields': [
                'missing_not_answered', 'missing_not_seen', 'missing_invalid'
            ]
        }
    ]


# ----------------------------------------------------------------------
# QUESTIONNAIRE STRUCTURE
# ----------------------------------------------------------------------
class QuestionnaireStructureUpdate(SurquestContextMixin, SurquestUpdateMixin,
                                   UpdateView):
    """View to display questionnaire structure (pages & questions)
    """

    model = Questionnaire
    template_name = 'ddm/admin/questionnaires/structure.html'
    form_class = QuestionnaireStructureForm
    inline_formsets = [
        {'label': None, 'formset': PageInlineFormSet}
    ]
    view_name = 'questionnaire-structure'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pages'] = Page.PAGE_TYPES
        return context


# ----------------------------------------------------------------------
# QUESTIONNAIRE TRIGGERS
# ----------------------------------------------------------------------
class QuestionnaireTriggerList(SurquestContextMixin, SurquestUpdateMixin,
                               UpdateView):
    """View to display list of triggers associated with current questionnaire.
    """

    model = Questionnaire
    template_name = 'ddm/admin/questionnaires/trigger_list.html'
    form_class = QuestionnaireStructureForm
    inline_formsets = [
        {'label': None, 'formset': TriggerInlineFormSet}
    ]
    view_name = 'questionnaire-triggers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_edit_link'] = True
        context['edit_link_label'] = 'Edit Trigger'
        context['triggers'] = Trigger.TRIGGER_TYPES
        return context


# ----------------------------------------------------------------------
# RESPONSES
# ----------------------------------------------------------------------
class QuestionnaireResponseView(SurquestContextMixin, TemplateView):
    """View to display responses belonging to the current questionnaire.
    """

    template_name = 'ddm/admin/questionnaires/responses.html'
    view_name = 'questionnaire-responses'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        questionnaire = Questionnaire.objects.get(pk=self.kwargs['pk'])
        q_vars = questionnaire.get_var_names(for_overview=True)
        q_subs = questionnaire.questionnairesubmission_set.all()
        q_sub_stats = questionnaire.get_submission_stats()

        submissions = q_subs[:10]

        sub_data = []
        for sub in submissions:
            sub_data.append(sub.get_related_responses(submission_fields=True))

        q_vars.insert(0, 'sub_session_id')
        q_vars.insert(0, 'sub_id')
        q_vars += ['sub_time_started', 'sub_time_submitted',
                   'sub_completion_time', 'sub_completed',
                   'sub_user_agent', 'sub_last_submitted_page']

        context['object'] = questionnaire
        context['questionnaire'] = questionnaire
        context['sub_data'] = sub_data
        context['questionnaire_vars'] = q_vars
        context['sub_stats'] = q_sub_stats
        return context


# ----------------------------------------------------------------------
# EXTERNAL VARIABLES
# ----------------------------------------------------------------------
class ExternalVariablesList(SurquestContextMixin, SurquestUpdateMixin, UpdateView):
    """View to display list of external variables associated with current
    questionnaire.
    """

    model = Questionnaire
    form_class = QuestionnaireStructureForm
    inline_formsets = [
        {'label': None, 'formset': external_variable_formset}
    ]
    template_name = (
        'ddm/admin/questionnaires/external_variables_list.html'
    )
    view_name = 'externalvariables-list'

    def get_success_url(self):
        return reverse(self.view_name, kwargs={'pk': self.object.pk})


# ----------------------------------------------------------------------
# UPLOADED DATA
# ----------------------------------------------------------------------
class UploadedDataView(SurquestContextMixin, TemplateView):
    """View to display uploaded data belonging to the current questionnaire.
    """

    template_name = 'ddm/admin/questionnaires/uploaded_data.html'
    view_name = 'uploaded-data'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # Get the current Questionnaire.
        questionnaire = Questionnaire.objects.get(pk=self.kwargs['pk'])
        context['object'] = questionnaire
        context['questionnaire'] = questionnaire

        # Get the file upload questions that belong to this questionnaire.
        fu_questions = FileUploadQuestion.objects.filter(
            page__questionnaire=questionnaire
        )
        context['file_upload_questions'] = fu_questions

        return context
