from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView

from ddm.admin_views import SurquestContextMixin
from ddm.forms import (
    TokenGeneratorForm, VariablesFromDataForm, CleanUploadTriggerForm,
    EmailTriggerForm
)
from ddm.models import (
    Questionnaire, TokenGenerator, VariablesFromData,
    CleanUploadDataTrigger, EmailTrigger
)


class TriggerCreateMixin(object):
    template_name = 'surquest/admin/triggers/create.html'
    view_name = None

    def __init__(self, *args, **kwargs):
        kwargs['view_name'] = self.model.DEFAULT_TRIGGER_TYPE + '-create'
        super().__init__(*args, **kwargs)

    def get_initial(self):
        questionnaire = Questionnaire.objects.get(pk=self.kwargs['q'])
        return {'questionnaire': questionnaire,}

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # Attach the questionnaire to the context.
        questionnaire = Questionnaire.objects.get(pk=self.kwargs['q'])
        context['questionnaire'] = questionnaire

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['qstnr_id'] = self.kwargs['q']
        return kwargs

    def get_success_url(self):
        return reverse('questionnaire-triggers',
                       kwargs={'pk': self.object.questionnaire.pk})


class TriggerUpdateMixin(object):
    template_name = 'surquest/admin/triggers/update.html'
    view_name = None

    def __init__(self, *args, **kwargs):
        kwargs['view_name'] = self.model.DEFAULT_TRIGGER_TYPE + '-update'
        super().__init__(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        instance = self.object
        context['questionnaire'] = instance.questionnaire
        return context

    def get_success_url(self):
        return reverse('questionnaire-triggers',
                       kwargs={'pk': self.object.questionnaire.pk})


# Token generator
# ----------------------------------------------------------------------
class TokenGeneratorCreate(TriggerCreateMixin, SurquestContextMixin,
                           LoginRequiredMixin, CreateView):
    """View to create a new token generator.
    """

    model = TokenGenerator
    form_class = TokenGeneratorForm


class TokenGeneratorUpdate(TriggerUpdateMixin, SurquestContextMixin,
                           LoginRequiredMixin, UpdateView):
    """View to update existing token generator.
    """

    model = TokenGenerator
    form_class = TokenGeneratorForm


# Variables from Data
# ----------------------------------------------------------------------
class VariablesFromDataCreate(TriggerCreateMixin, SurquestContextMixin,
                              LoginRequiredMixin, CreateView):
    """View to create a new 'Variables from Data' trigger.
    """

    model = VariablesFromData
    form_class = VariablesFromDataForm


class VariablesFromDataUpdate(TriggerUpdateMixin, SurquestContextMixin,
                              LoginRequiredMixin, UpdateView):
    """View to update existing 'Variables from Data' trigger.
    """

    model = VariablesFromData
    form_class = VariablesFromDataForm


# Email Trigger
# ----------------------------------------------------------------------
class EmailTriggerCreate(TriggerCreateMixin, SurquestContextMixin,
                         LoginRequiredMixin, CreateView):
    """View to create a new email trigger.
    """

    model = EmailTrigger
    form_class = EmailTriggerForm


class EmailTriggerUpdate(TriggerUpdateMixin, SurquestContextMixin,
                         LoginRequiredMixin, UpdateView):
    """View to update existing email trigger.
    """

    model = EmailTrigger
    form_class = EmailTriggerForm


# Clean Upload Data Trigger
# ----------------------------------------------------------------------
class CleanUploadTriggerCreate(TriggerCreateMixin, SurquestContextMixin,
                               LoginRequiredMixin, CreateView):
    """View to create a new upload data cleaning trigger.
    """

    model = CleanUploadDataTrigger
    form_class = CleanUploadTriggerForm


class CleanUploadTriggerUpdate(TriggerUpdateMixin, SurquestContextMixin,
                               LoginRequiredMixin, UpdateView):
    """View to update existing upload data cleaning trigger.
    """

    model = CleanUploadDataTrigger
    form_class = CleanUploadTriggerForm
