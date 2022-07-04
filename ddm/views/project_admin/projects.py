from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.forms import ProjectCreateForm
from ddm.models import DonationProject, ResearchProfile
from ddm.views.project_admin.auth import DdmAuthMixin


class ProjectList(DdmAuthMixin, ListView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/list.html'

    def get_queryset(self):
        return DonationProject.objects.filter(owner__user=self.request.user)


class ProjectCreate(SuccessMessageMixin, DdmAuthMixin, CreateView):
    """ View to create a new donation project. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/create.html'
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
    template_name = 'ddm/project_admin/project/detail.html'


class ProjectEdit(SuccessMessageMixin, DdmAuthMixin, UpdateView):
    """ View to edit the details of an existing donation project. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/edit.html'
    fields = ['name', 'slug']
    success_message = 'Project details successfully updated.'


class ProjectDelete(DdmAuthMixin, DeleteView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/delete.html'
    success_url = reverse_lazy('project-list')
    success_message = 'Project was deleted.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class WelcomePageEdit(SuccessMessageMixin, DdmAuthMixin, UpdateView):
    """ View to edit the welcome page. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/edit-welcome.html'
    fields = ['intro_text']
    success_message = 'Welcome Page successfully updated.'


class EndPageEdit(SuccessMessageMixin, DdmAuthMixin, UpdateView):
    """ View to edit the welcome page. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/edit-end.html'
    fields = ['outro_text']
    success_message = 'End Page successfully updated.'
