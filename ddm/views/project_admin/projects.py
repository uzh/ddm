from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.models import DonationProject, DonationBlueprint, ZippedBlueprint


class ProjectList(LoginRequiredMixin, ListView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/list.html'


class ProjectCreate(LoginRequiredMixin, CreateView):
    """ View to create a new donation project. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/create.html'
    fields = ['name', 'slug']


class ProjectDetail(LoginRequiredMixin, DetailView):
    """ View to display landing page for project. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/detail.html'


class ProjectEdit(LoginRequiredMixin, UpdateView):
    """ View to edit the details of an existing donation project. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/edit.html'
    fields = ['name', 'slug']


class ProjectDelete(LoginRequiredMixin, DeleteView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/delete.html'
    success_url = reverse_lazy('project-list')


class WelcomePageEdit(LoginRequiredMixin, UpdateView):
    """ View to edit the welcome page. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/edit.html'
    fields = ['intro_text']


class EndPageEdit(LoginRequiredMixin, UpdateView):
    """ View to edit the welcome page. """
    model = DonationProject
    template_name = 'ddm/project_admin/project/edit.html'
    fields = ['outro_text']
