from django.contrib.messages.views import SuccessMessageMixin
from django.forms import inlineformset_factory
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django_ckeditor_5.widgets import CKEditor5Widget

from ddm.auth.views import DDMAuthMixin
from ddm.datadonation.models import DonationBlueprint
from ddm.projects.models import DonationProject
from ddm.questionnaire.forms import FilterConditionForm
from ddm.questionnaire.models import (
    QuestionBase, QuestionType, SingleChoiceQuestion, MultiChoiceQuestion,
    OpenQuestion, MatrixQuestion, SemanticDifferential, Transition,
    QuestionItem, ScalePoint, FilterCondition
)


class ProjectMixin:
    """ Mixin for all blueprint related views. """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'project_url_id': self.kwargs['project_url_id']})
        context.update({'project': self.get_project()})
        return context

    def get_project(self):
        return DonationProject.objects.get(url_id=self.kwargs['project_url_id'])


class QuestionnaireOverview(ProjectMixin, DDMAuthMixin, ListView):
    """ View to list all donation blueprints associated with a project. """
    model = DonationBlueprint
    context_object_name = 'donation_blueprints'
    template_name = 'ddm_questionnaire/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_types = QuestionType.choices
        context.update({
            'question_types': question_types,
            'questions': self.get_all_questions()
        })
        return context

    def get_all_questions(self):
        project = self.get_project()
        return project.questionbase_set.all()

    def get_queryset(self):
        return super().get_queryset().filter(
            project__url_id=self.kwargs['project_url_id'])


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

    SHARED_FIELDS = [
        'name',
        'blueprint',
        'page',
        'index',
        'variable_name',
        'text',
        'required'
    ]
    QUESTION_FIELDS = {
        'single_choice': SHARED_FIELDS + ['randomize_items'],
        'multi_choice': SHARED_FIELDS + ['randomize_items'],
        'matrix': SHARED_FIELDS + ['randomize_items', 'show_scale_headings'],
        'semantic_diff': SHARED_FIELDS + ['randomize_items'],
        'open': SHARED_FIELDS + ['input_type', 'max_input_length', 'display', 'multi_item_response', 'randomize_items'],
        'transition': SHARED_FIELDS
    }

    def get_queryset(self):
        self.model = self.QUESTION_CLASSES[self.kwargs['question_type']]
        self.fields = self.QUESTION_FIELDS[self.kwargs['question_type']]
        return super().get_queryset()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.kwargs['question_type'] == 'transition':
            del form.fields['required']
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_type_label = QuestionType(self.kwargs['question_type']).label
        context.update({'question_type': question_type_label})
        context['form'].fields['blueprint'].queryset = DonationBlueprint.objects.filter(
            project__url_id=self.kwargs['project_url_id'])
        context['form'].fields['blueprint'].empty_label = 'General Question – no Blueprint assigned'
        context['form'].fields['text'].widget = CKEditor5Widget(config_name='ddm_ckeditor_temp_func')
        return context


class QuestionCreate(SuccessMessageMixin, DDMAuthMixin, QuestionFormMixin, CreateView):
    """ View to create question. """
    template_name = 'ddm_questionnaire/create.html'
    success_message = 'New %(question_type)s was created.'

    def get_initial(self):
        initial = super().get_initial()
        initial['question_type'] = self.kwargs['question_type']
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.QUESTION_CLASSES[self.kwargs['question_type']](
            project=self.get_project(),
        )
        return kwargs

    def get_success_url(self):
        kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': self.kwargs['question_type'],
            'pk': self.object.pk
        }
        return reverse('ddm_questionnaire:edit', kwargs=kwargs)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            question_type=self.QUESTION_CLASSES[self.kwargs['question_type']].DEFAULT_QUESTION_TYPE.label
        )


class QuestionEdit(SuccessMessageMixin, DDMAuthMixin, QuestionFormMixin, UpdateView):
    """ View to edit question. """
    model = QuestionBase
    template_name = 'ddm_questionnaire/edit.html'
    success_message = 'Question "%(name)s" was successfully updated.'

    def get_success_url(self):
        success_kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': self.kwargs['question_type'],
            'pk': self.kwargs['pk']
        }
        return reverse('ddm_questionnaire:edit', kwargs=success_kwargs)


class QuestionDelete(SuccessMessageMixin, DDMAuthMixin, ProjectMixin, DeleteView):
    """ View to delete question. """
    model = QuestionBase
    template_name = 'ddm_questionnaire/delete.html'
    success_message = 'Question "%s" was deleted.'

    def get_success_message(self, cleaned_data):
        return self.success_message % self.object.name

    def get_success_url(self):
        return reverse(
        'ddm_questionnaire:overview', kwargs={'project_url_id': self.kwargs['project_url_id']})


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

    def get_initial_extra_data(self):
        """ Placeholder function to overwrite in views. """
        return []

    def get_n_extra_forms(self):
        """ Placeholder function to overwrite in views. """
        return 0

    def get_formset(self):
        n_extra = self.get_n_extra_forms()
        formset = inlineformset_factory(
            QuestionBase, self.formset_model, exclude=self.get_excluded_fields(),
            extra=n_extra
        )
        if self.request.method == "GET":
            initial_data = self.get_initial_extra_data()
        else:
            initial_data = None
        return formset(self.request.POST or None, instance=self.object, initial=initial_data)

    def get_excluded_fields(self):
        if not isinstance(self.object, SemanticDifferential):
            excluded_fields = ('label_alt',)
        else:
            excluded_fields = ()
        return excluded_fields


class ItemEdit(SuccessMessageMixin, DDMAuthMixin, InlineFormsetMixin, UpdateView):
    """ View to edit the items associated with a question. """
    model = QuestionBase
    formset_model = QuestionItem
    template_name = 'ddm_questionnaire/edit_set.html'
    context_title = 'Items'
    success_message = 'Question items updated.'

    def get_initial_extra_data(self):
        if self.object.questionitem_set.all().count() == 0:
            return [{'index': 1}]
        else:
            return []

    def get_n_extra_forms(self):
        """ Placeholder function to overwrite in views. """
        if self.object.questionitem_set.all().count() == 0:
            return 1
        else:
            return 0

    def get_success_url(self):
        question = self.get_object()
        success_kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': question.question_type,
            'pk': question.pk
        }
        return reverse('ddm_questionnaire:items', kwargs=success_kwargs)


class ScaleEdit(SuccessMessageMixin, DDMAuthMixin, InlineFormsetMixin, UpdateView):
    """ View to edit the scale associated with a question. """
    model = QuestionBase
    formset_model = ScalePoint
    template_name = 'ddm_questionnaire/edit_set.html'
    context_title = 'Scale Points'
    success_message = 'Question scale updated.'

    def get_initial_extra_data(self):
        if self.object.scalepoint_set.all().count() == 0:
            return [{'index': 1}]
        else:
            return []

    def get_n_extra_forms(self):
        """ Placeholder function to overwrite in views. """
        if self.object.scalepoint_set.all().count() == 0:
            return 1
        else:
            return 0

    def get_success_url(self):
        question = self.get_object()
        success_kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': question.question_type,
            'pk': question.pk
        }
        return reverse('ddm_questionnaire:scale', kwargs=success_kwargs)


class FilterEditBase(SuccessMessageMixin, ProjectMixin, DDMAuthMixin, UpdateView):
    formset_model = FilterCondition
    fields = []
    context_title = 'Filter Conditions'
    success_message = 'Filter conditions updated.'

    def get_filters(self):
        return self.object.filtercondition_set.all()

    def get_project(self):
        """Placeholder function."""
        return None

    def get_formset(self):
        """
        Creates a FilterConditionFormset and adds the target depending on the
        information passed to the view.
        """
        if isinstance(self.object, QuestionBase):
            fk_name = 'target_question'
            fk_class = QuestionBase
        elif isinstance(self.object, QuestionItem):
            fk_name = 'target_item'
            fk_class = QuestionItem
        else:
            raise ValueError('Provided object must be QuestionBase or QuestionItem.')

        if self.request.method == 'GET':
            # Check if an extra form must be rendered.
            filters = [f for f in self.get_filters() if f.check_source_exists()]
            if len(filters) == 0:
                n_extra = 1
            else:
                n_extra = 0

            initial_data = self.get_initial_extra_data()
        else:
            n_extra = 0
            initial_data = self.get_initial_extra_data()

        formset_factory = inlineformset_factory(
            fk_class,
            FilterCondition,
            form=FilterConditionForm,
            exclude=['target_question', 'target_item'],
            extra=n_extra,
            can_delete=True,
            fk_name=fk_name
        )

        formset = formset_factory(
            self.request.POST or None,
            instance=self.object,
            initial=initial_data,
            form_kwargs={'project': self.get_project(), 'target_object': self.object}
        )

        return formset

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

    def get_initial_extra_data(self):
        return []


class FilterEditQuestion(FilterEditBase):
    model = QuestionBase
    template_name = 'ddm_questionnaire/edit_set.html'

    def get_project(self):
        return self.object.project

    def get_success_url(self):
        question = self.get_object()
        success_kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': question.question_type,
            'pk': question.pk
        }
        return reverse('ddm_questionnaire:question_filters', kwargs=success_kwargs)


class FilterEditItems(FilterEditBase):
    model = QuestionItem
    template_name = 'ddm_questionnaire/edit_item_set.html'

    def get_project(self):
        return self.object.question.project

    def get_success_url(self):
        item = self.get_object()
        success_kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': item.question.question_type,
            'question_pk': item.question.pk,
            'pk': item.pk
        }
        return reverse('ddm_questionnaire:item_filters', kwargs=success_kwargs)
