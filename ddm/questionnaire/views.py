from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import QuerySet
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.text import Truncator
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from ddm.auth.views import DDMAuthMixin
from ddm.core.view_mixins import DDMContextMixin
from ddm.datadonation.models import DonationBlueprint
from ddm.projects.models import DonationProject
from ddm.questionnaire.forms import (
    FilterConditionForm,
    get_question_form,
    QuestionItemInlineFormset,
    ScalePointInlineFormset
)
from ddm.questionnaire.models import (
    QuestionBase, SingleChoiceQuestion, MultiChoiceQuestion,
    OpenQuestion, MatrixQuestion, SemanticDifferential, Transition,
    QuestionItem, FilterCondition
)
from ddm.questionnaire.constants import QuestionType


class ProjectMixin(DDMContextMixin):
    """ Mixin for all blueprint related views. """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'project_url_id': self.kwargs['project_url_id']})
        context.update({'project': self.get_project()})
        return context

    def get_project(self) -> DonationProject:
        return DonationProject.objects.get(url_id=self.kwargs['project_url_id'])

    def get_breadcrumbs(self):
        project = self.get_project()
        name = Truncator(project.name).chars(15)
        return [
            ('Projects', reverse_lazy('ddm_projects:list')),
            (
                f'{name}',
                reverse(
                    'ddm_projects:detail',
                    kwargs={'project_url_id': self.kwargs['project_url_id']}
                )
            ),
        ]


class QuestionnaireOverview(ProjectMixin, DDMAuthMixin, ListView):
    """ View to list all donation blueprints associated with a project. """
    model = DonationBlueprint
    context_object_name = 'donation_blueprints'
    template_name = 'ddm_questionnaire/question_list.html'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append(('Questionnaire', None))
        return crumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_types = QuestionType.choices
        context.update({
            'question_types': question_types,
            'questions': self.get_all_questions(),
            'pages': self.get_questions_per_page()
        })
        return context

    def get_questions_per_page(self):
        questions = self.get_all_questions()
        if not questions:
            return questions

        pages = questions.values_list('page', flat=True).order_by('page')
        q_per_page = {}
        for page in set(pages):
            q_per_page[page] = questions.filter(page=page)
        return q_per_page

    def get_all_questions(self) -> QuerySet[QuestionBase]:
        project = self.get_project()
        return project.questionbase_set.all()

    def get_queryset(self) -> QuerySet[DonationBlueprint]:
        return super().get_queryset().filter(
            project__url_id=self.kwargs['project_url_id'])


class QuestionFormMixin(ProjectMixin):

    QUESTION_CLASSES = {
        'single_choice': SingleChoiceQuestion,
        'multi_choice': MultiChoiceQuestion,
        'open': OpenQuestion,
        'matrix': MatrixQuestion,
        'semantic_diff': SemanticDifferential,
        'transition': Transition
    }

    def get_form_class(self):
        return get_question_form(self.question_type)

    @property
    def question_type(self):
        return self.kwargs.get('question_type')

    @property
    def project_url_id(self):
        return self.kwargs.get('project_url_id')

    @property
    def question_class(self):
        return self.QUESTION_CLASSES[self.question_type]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_type_label = QuestionType(self.question_type).label
        context.update({'question_type': question_type_label})
        context['form'].fields['blueprint'].queryset = DonationBlueprint.objects.filter(
            project__url_id=self.project_url_id)
        return context


class QuestionCreate(
    SuccessMessageMixin,
    DDMAuthMixin,
    QuestionFormMixin,
    CreateView
):
    """ View to create question. """
    template_name = 'ddm_questionnaire/question_create.html'
    success_message = 'New %(question_type)s was created.'

    submit_label = 'Create Question'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append((
            'Questionnaire',
            reverse(
                'ddm_questionnaire:overview',
                kwargs={'project_url_id': self.kwargs['project_url_id']}
            )
        ))
        crumbs.append(('Create Question', None))
        return crumbs

    def get_initial(self) -> dict:
        initial = super().get_initial()
        initial['question_type'] = self.question_type
        return initial

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.question_class(project=self.get_project())
        kwargs['use_required_attribute'] = False
        return kwargs

    def get_success_url(self) -> str:
        kwargs = {
            'project_url_id': self.project_url_id,
            'question_type': self.question_type,
            'pk': self.object.pk
        }
        return reverse('ddm_questionnaire:edit', kwargs=kwargs)

    def get_success_message(self, cleaned_data) -> str:
        return self.success_message % dict(
            cleaned_data,
            question_type=self.question_class.DEFAULT_QUESTION_TYPE.label
        )


class QuestionEdit(SuccessMessageMixin, DDMAuthMixin, QuestionFormMixin, UpdateView):
    """ View to edit question. """
    model = QuestionBase
    template_name = 'ddm_questionnaire/question_edit.html'
    success_message = 'Question "%(name)s" was successfully updated.'

    submit_label = 'Update Question'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append((
            'Questionnaire',
            reverse(
                'ddm_questionnaire:overview',
                kwargs={'project_url_id': self.kwargs['project_url_id']}
            )
        ))
        crumbs.append(('Edit', None))
        return crumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'item_formset': self.get_item_formset(),
            'scale_formset': self.get_scale_point_formset(),
        })
        return context

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs['use_required_attribute'] = False
        return kwargs

    def get_item_formset(self, data=None):
        if self.question_type in ['transition']:
            return None

        show_label_alt = isinstance(self.object, SemanticDifferential)

        return QuestionItemInlineFormset(
            data,
            instance=self.object,
            queryset=self.object.questionitem_set.all().order_by('index'),
            show_label_alt=show_label_alt,
        )

    def get_scale_point_formset(self, data=None):
        if self.question_type not in ['matrix', 'semantic_diff']:
            return None

        return ScalePointInlineFormset(
            data,
            instance=self.object,
            queryset=self.object.scalepoint_set.all().order_by('index'),
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        item_formset = self.get_item_formset(self.request.POST)
        scale_formset = self.get_scale_point_formset(self.request.POST)

        if form.is_valid():
            if item_formset and not item_formset.is_valid():
                return self.form_invalid(form, item_formset, scale_formset)
            if scale_formset and not scale_formset.is_valid():
                return self.form_invalid(form, item_formset, scale_formset)
            return self.form_valid(form, item_formset, scale_formset)
        else:
            return self.form_invalid(form, item_formset, scale_formset)

    def form_valid(self, form, item_formset, scale_formset):
        with transaction.atomic():
            self.object = form.save()
            if item_formset:
                item_formset.instance = self.object
                item_formset.save()
            if scale_formset:
                scale_formset.instance = self.object
                scale_formset.save()

        # Needed, because super().form_valid() is not called
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, item_formset, scale_formset):
        context = self.get_context_data(
            form=form,
            item_formset=item_formset,
            scale_formset=scale_formset,
        )
        return self.render_to_response(context)

    def get_success_url(self) -> str:
        success_kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': self.question_type,
            'pk': self.kwargs['pk']
        }
        return reverse('ddm_questionnaire:edit', kwargs=success_kwargs)


class QuestionDelete(SuccessMessageMixin, DDMAuthMixin, ProjectMixin, DeleteView):
    """ View to delete question. """
    model = QuestionBase
    template_name = 'ddm_questionnaire/question_delete.html'
    success_message = 'Question "%s" was deleted.'

    submit_label = 'Delete Question'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append((
            'Questionnaire',
            reverse('ddm_questionnaire:overview', kwargs={'project_url_id': self.kwargs['project_url_id']})
        ))
        crumbs.append((
            f'Question "{Truncator(self.object.name).chars(15)}"',
             reverse(
                 'ddm_questionnaire:edit',
                 kwargs={
                     'project_url_id': self.kwargs['project_url_id'],
                     'question_type': self.object.question_type,
                     'pk': self.object.pk
                 }
             )
        ))
        crumbs.append(('Delete', None))
        return crumbs

    def get_success_message(self, cleaned_data) -> str:
        return self.success_message % self.object.name

    def get_success_url(self) -> str:
        return reverse(
        'ddm_questionnaire:overview',
            kwargs={'project_url_id': self.kwargs['project_url_id']}
        )


class FilterEditBase(SuccessMessageMixin, ProjectMixin, DDMAuthMixin, UpdateView):
    formset_model = FilterCondition
    fields = []
    success_message = 'Filter conditions updated'
    target_type = None

    submit_label = 'Update Filters'

    def get_filters(self) -> QuerySet[FilterCondition]:
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
            'question': self.object,
            'target_type': self.target_type
        })
        return context

    def get_initial_extra_data(self) -> list:
        return []


class FilterEditQuestion(FilterEditBase):
    model = QuestionBase
    template_name = 'ddm_questionnaire/filter_conditions_edit.html'
    target_type = 'Question'

    def get_project(self) -> DonationProject:
        return self.object.project

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append((
            'Questionnaire',
            reverse(
                'ddm_questionnaire:overview',
                kwargs={'project_url_id': self.kwargs['project_url_id']}
            )
        ))
        crumbs.append(('Question', reverse('ddm_questionnaire:edit', kwargs={
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': self.object.question_type,
            'pk': self.object.pk,
        })))
        crumbs.append(('Filter Configuration', None))
        return crumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'target_name': self.object.name,
        })
        return context

    def get_success_url(self) -> str:
        question = self.get_object()
        success_kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': question.question_type,
            'pk': question.pk
        }
        return reverse('ddm_questionnaire:question_filters', kwargs=success_kwargs)


class FilterEditItems(FilterEditBase):
    model = QuestionItem
    template_name = 'ddm_questionnaire/filter_conditions_edit.html'
    target_type = 'Item'

    def get_project(self) -> DonationProject:
        return self.object.question.project

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append((
            'Questionnaire',
            reverse(
                'ddm_questionnaire:overview',
                kwargs={'project_url_id': self.kwargs['project_url_id']}
            )
        ))
        crumbs.append(('Question', reverse('ddm_questionnaire:edit', kwargs={
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': self.object.question.question_type,
            'pk': self.object.question.pk,
        })))
        crumbs.append(('Filter Configuration', None))
        return crumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'target_name': self.object.label,
            'question': self.object.question,
        })
        return context

    def get_success_url(self) -> str:
        item = self.get_object()
        success_kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'question_type': item.question.question_type,
            'question_pk': item.question.pk,
            'pk': item.pk
        }
        return reverse('ddm_questionnaire:item_filters', kwargs=success_kwargs)
