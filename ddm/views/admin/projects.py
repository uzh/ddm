from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView

from ddm.forms import APITokenCreationForm, ProjectCreateForm
from ddm.models.auth import ProjectAccessToken
from ddm.models.core import DonationProject, ResearchProfile
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
        'img_header_left', 'img_header_right'
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


class ProjectLogsView(SuccessMessageMixin, DdmAuthMixin, TemplateView):
    """ View that lists all exceptions related to a project. """
    template_name = 'ddm/admin/project/project_logs/overview.html'

    def get_project(self):
        project_id = self.kwargs.get('project_pk')
        return DonationProject.objects.filter(pk=project_id).first()

    def get_event_logs(self):
        project = self.get_project()
        return project.eventlogentry_set.all()

    def get_exception_logs(self):
        project = self.get_project()
        return project.exceptionlogentry_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'project': self.get_project(),
            'events': self.get_event_logs(),
            'exceptions': self.get_exception_logs()
        })
        return context


class ProjectAPITokenView(SuccessMessageMixin, DdmAuthMixin, FormView):
    """ View to see existing access token or generate a new one. """
    template_name = 'ddm/admin/project/token.html'
    form_class = APITokenCreationForm

    def get_project(self):
        """ Returns current project. """
        project_id = self.kwargs.get('pk')
        return DonationProject.objects.filter(pk=project_id).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context.update({
            'project': project,
            'token': ProjectAccessToken.objects.filter(project=project).first()
        })
        return context

    def form_valid(self, form):
        """ If form is valid, either create new token or delete existing one. """
        project = self.get_project()
        if form.cleaned_data['action'] == 'create':
            project.create_token(expiration_days=form.cleaned_data['expiration_days'])

        if form.cleaned_data['action'] == 'delete':
            token = project.get_token()
            token.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project-token', kwargs={'pk': self.kwargs.get('pk')})
