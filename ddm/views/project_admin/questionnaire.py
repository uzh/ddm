from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from ddm.models import (
    QuestionBase, QuestionType, SingleChoiceQuestion, MultiChoiceQuestion,
    OpenQuestion, MatrixQuestion, SemanticDifferential, Transition, QuestionItem,
    ScalePoint
)
from . import ProjectBlueprintList


class ProjectMixin:
    """ Mixin for all blueprint related views. """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'project_pk': self.kwargs['project_pk']})
        return context


class QuestionnaireOverview(ProjectBlueprintList):
    """ View to list all donation blueprints associated with a project. """
    template_name = 'ddm/project_admin/questionnaire/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_types = QuestionType.choices
        context.update({'question_types': question_types})
        return context


class QuestionFormMixin(ProjectMixin):
    model = None
    fields = '__all__'

    QUESTION_CLASSES = {
        'single_choice': SingleChoiceQuestion,
        'multi_choice': MultiChoiceQuestion,
        'open': OpenQuestion,
        'matrix': MatrixQuestion,
        'semantic_diff': SemanticDifferential,
        'transition': Transition
    }

    SHARED_FIELDS = ['name', 'blueprint', 'index', 'variable_name', 'text', 'required']
    QUESTION_FIELDS = {
        'single_choice': SHARED_FIELDS + ['randomize_items'],
        'multi_choice': SHARED_FIELDS + ['randomize_items'],
        'matrix': SHARED_FIELDS + ['randomize_items'],
        'semantic_diff': SHARED_FIELDS + ['randomize_items'],
        'open': SHARED_FIELDS,
        'transition': SHARED_FIELDS
    }

    def get_queryset(self):
        self.model = self.QUESTION_CLASSES[self.kwargs['question_type']]
        self.fields = self.QUESTION_FIELDS[self.kwargs['question_type']]
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_type_label = QuestionType(self.kwargs['question_type']).label
        context.update({'question_type': question_type_label})
        return context


class QuestionCreate(LoginRequiredMixin, QuestionFormMixin, CreateView):
    """ View to create question. """
    template_name = 'ddm/project_admin/questionnaire/create.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['question_type'] = self.kwargs['question_type']
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.QUESTION_CLASSES[self.kwargs['question_type']](
            project_id=self.kwargs['project_pk'],
        )
        return kwargs

    def get_success_url(self):
        return reverse('questionnaire-overview', kwargs={'project_pk': self.kwargs['project_pk']})


class QuestionEdit(LoginRequiredMixin, QuestionFormMixin, UpdateView):
    """ View to edit question. """
    model = QuestionBase
    template_name = 'ddm/project_admin/questionnaire/edit.html'
    fields = '__all__'


class QuestionDelete(LoginRequiredMixin, ProjectMixin, DeleteView):
    """ View to delete question. """
    model = QuestionBase
    template_name = 'ddm/project_admin/questionnaire/delete.html'

    def get_success_url(self):
        return reverse('questionnaire-overview', kwargs={'project_pk': self.kwargs['project_pk']})


class InlineFormsetMixin(ProjectMixin):
    model = QuestionBase
    fields = '__all__'
    formset_model = None
    context_title = None
    fields_to_exclude = ()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = self.get_formset()
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return super().form_invalid(formset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'formset': self.get_formset(),
            'context_title': self.context_title,
            'question': self.object
        })
        return context

    def get_formset(self):
        formset = inlineformset_factory(
            QuestionBase, self.formset_model, exclude=self.get_excluded_fields(),
            extra=1
        )
        return formset(self.request.POST or None, instance=self.object)

    def get_excluded_fields(self):
        if not isinstance(self.object, SemanticDifferential):
            excluded_fields = ('label_alt',)
        else:
            excluded_fields = ()
        return excluded_fields

    def get_success_url(self):
        question = self.get_object()
        success_kwargs = {
            'project_pk': self.kwargs['project_pk'],
            'question_type': question.question_type,
            'pk': question.pk
        }
        return reverse('question-edit', kwargs=success_kwargs)


class ItemEdit(LoginRequiredMixin, InlineFormsetMixin, UpdateView):
    """ View to edit the items associated with a question. """
    model = QuestionBase
    formset_model = QuestionItem
    template_name = 'ddm/project_admin/questionnaire/edit_set.html'
    context_title = 'Items'


class ScaleEdit(LoginRequiredMixin, InlineFormsetMixin, UpdateView):
    """ View to edit the scale associated with a question. """
    model = QuestionBase
    formset_model = ScalePoint
    template_name = 'ddm/project_admin/questionnaire/edit_set.html'
    context_title = 'Scale Points'
