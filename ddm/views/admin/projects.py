from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.forms import ProjectCreateForm
from ddm.models.core import DonationProject, ResearchProfile
from ddm.models.exceptions import ExceptionLogEntry
from ddm.views.admin.auth import DdmAuthMixin


class ProjectList(DdmAuthMixin, ListView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    template_name = 'ddm/admin/project/list.html'

    def get_queryset(self):
        return DonationProject.objects.filter(owner__user=self.request.user)


class ProjectCreate(SuccessMessageMixin, DdmAuthMixin, CreateView):
    """ View to create a new donation project. """
    model = DonationProject
    template_name = 'ddm/admin/project/create.html'
    form_class = ProjectCreateForm
    success_message = 'Project was created successfully.'

    def get_initial(self):
        self.initial = super().get_initial()
        self.initial.update({'owner': ResearchProfile.objects.get(user=self.request.user)})
        return self.initial

    def form_valid(self, form):
        form.instance.owner = ResearchProfile.objects.get(user=self.request.user)
        return super().form_valid(form)


class ProjectDetail(DdmAuthMixin, DetailView):
    """ View to display landing page for project. """
    model = DonationProject
    template_name = 'ddm/admin/project/detail.html'


class ProjectEdit(SuccessMessageMixin, DdmAuthMixin, UpdateView):
    """ View to edit the details of an existing donation project. """
    model = DonationProject
    template_name = 'ddm/admin/project/edit.html'
    fields = [
        'name', 'slug', 'contact_information', 'data_protection_statement',
        'url_parameter_enabled', 'expected_url_parameters',
        'redirect_enabled', 'redirect_target',
    ]
    success_message = 'Project details successfully updated.'

    def form_valid(self, form):
        if form.cleaned_data['url_parameter_enabled'] and form.cleaned_data['expected_url_parameters'] == '':
            form.add_error('expected_url_parameters', 'URL parameter is enabled but no parameter is defined.')

        if form.cleaned_data['redirect_enabled'] and form.cleaned_data['redirect_target'] == '':
            form.add_error('redirect_target', 'Redirect is enabled but no redirect target is defined.')

        if form.is_valid():
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ProjectDelete(DdmAuthMixin, DeleteView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    template_name = 'ddm/admin/project/delete.html'
    success_url = reverse_lazy('project-list')
    success_message = 'Project was deleted.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class BriefingEdit(SuccessMessageMixin, DdmAuthMixin, UpdateView):
    """ View to edit the briefing page. """
    model = DonationProject
    template_name = 'ddm/admin/project/edit-briefing.html'
    fields = ['briefing_text', 'briefing_consent_enabled', 'briefing_consent_label_yes', 'briefing_consent_label_no']
    success_message = 'Briefing page successfully updated.'

    def form_valid(self, form):
        consent_label_error_msg = 'When briefing consent is enabled, a consent label must be provided.'
        if form.cleaned_data['briefing_consent_enabled'] and form.cleaned_data['briefing_consent_label_yes'] == '':
            form.add_error('briefing_consent_label_yes', consent_label_error_msg)

        if form.cleaned_data['briefing_consent_enabled'] and form.cleaned_data['briefing_consent_label_no'] == '':
            form.add_error('briefing_consent_label_no', consent_label_error_msg)

        if form.is_valid():
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class DebriefingEdit(SuccessMessageMixin, DdmAuthMixin, UpdateView):
    """ View to edit the debriefing page. """
    model = DonationProject
    template_name = 'ddm/admin/project/edit-debriefing.html'
    fields = ['debriefing_text']
    success_message = 'Debriefing page successfully updated.'


class ExceptionList(SuccessMessageMixin, DdmAuthMixin, ListView):
    """ View that lists all exceptions related to a project. """
    model = ExceptionLogEntry
    template_name = 'ddm/admin/project/exceptions.html'
    context_object_name = 'exceptions'

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.kwargs.get('project_pk')
        if project_id is not None:
            project = DonationProject.objects.get(pk=project_id)
            qs = qs.filter(project=project).order_by('-date')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_pk')
        if project_id is not None:
            project = DonationProject.objects.get(pk=project_id)
        else:
            project = None
        context.update({'project': project})
        return context
