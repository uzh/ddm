from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ddm.admin_views import SurquestContextMixin, SurquestUpdateMixin
from ddm.forms import QuestionPageForm, EndPageForm, QuestionInlineFormset
from ddm.models import Questionnaire, Question, EndPage, QuestionPage


class PageCreateMixin(object):
    template_name = 'surquest/admin/pages/create.html'
    view_name = None

    def __init__(self, *args, **kwargs):
        kwargs['view_name'] = self.model.DEFAULT_PAGE_TYPE + '-create'
        super().__init__(*args, **kwargs)

    def get_initial(self):
        questionnaire = Questionnaire.objects.get(pk=self.kwargs['q'])
        return {'questionnaire': questionnaire}

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['questionnaire'] = Questionnaire.objects.get(pk=self.kwargs['q'])
        return context


class PageUpdateMixin(object):
    template_name = 'surquest/admin/pages/update.html'
    view_name = None

    def __init__(self, *args, **kwargs):
        kwargs['view_name'] = self.model.DEFAULT_PAGE_TYPE + '-update'
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse(self.view_name,
                       kwargs={'pk': self.object.pk,
                               'q': self.object.questionnaire.pk})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        instance = self.object
        context['questionnaire'] = instance.questionnaire
        context['page'] = instance
        context['questions'] = Question.QUESTION_TYPES
        context['show_edit_link'] = True

        return context


# Question Page
# ----------------------------------------------------------------------
class QuestionPageCreate(LoginRequiredMixin, SurquestContextMixin,
                         PageCreateMixin, CreateView):
    """
    """
    model = QuestionPage
    form_class = QuestionPageForm


class QuestionPageUpdate(SurquestContextMixin, SurquestUpdateMixin,
                         PageUpdateMixin, UpdateView):
    """
    """
    model = QuestionPage
    form_class = QuestionPageForm
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': ['questionnaire', 'name', 'show_back_button']
        },
        {
            'name': 'Questions on Page',
            'description': 'Description of Questions on Page',
            'type': 'inline_form',
            'formset_class': QuestionInlineFormset
        },
    ]


class QuestionPageDelete(LoginRequiredMixin, SurquestContextMixin,
                         PageUpdateMixin, DeleteView):
    """
    """
    model = QuestionPage
    template_name = 'surquest/admin/pages/delete.html'
    view_name = model.DEFAULT_PAGE_TYPE + '-delete'

    def get_success_url(self):
        return reverse('questionnaire-structure',
                       kwargs={'pk': self.object.questionnaire.pk})


# Question Page
# ----------------------------------------------------------------------
class EndPageCreate(LoginRequiredMixin, SurquestContextMixin,
                    PageCreateMixin, CreateView):
    """
    """
    model = EndPage
    form_class = EndPageForm


class EndPageUpdate(SurquestContextMixin, SurquestUpdateMixin, PageUpdateMixin,
                    UpdateView):
    """
    """
    model = EndPage
    form_class = EndPageForm
    fieldsets = [
        {
            'name': 'Basic Information',
            'description': 'Description of Basic Information',
            'type': 'basic_form',
            'fields': ['questionnaire', 'name', 'show_back_button']
        },
        {
            'name': 'Redirect Options',
            'description': 'Description of redirect option section.',
            'type': 'basic_form',
            'fields': ['redirect', 'redirect_url']
        },
        {
            'name': 'Questions on Page',
            'description': 'Description of Questions on Page',
            'type': 'inline_form',
            'formset_class': QuestionInlineFormset
        },
    ]


class EndPageDelete(LoginRequiredMixin, SurquestContextMixin,
                    PageUpdateMixin, DeleteView):
    """
    """
    model = EndPage
    template_name = 'surquest/admin/pages/delete.html'
    view_name = model.DEFAULT_PAGE_TYPE + '-delete'

    def get_success_url(self):
        return reverse('questionnaire-structure',
                       kwargs={'pk': self.object.questionnaire.pk})
