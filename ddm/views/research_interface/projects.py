from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.models import DonationProject


class ProjectList(LoginRequiredMixin, ListView):
    """ View to display a list of existing donation projects.
    """
    model = DonationProject
    template_name = 'ddm/research_interface/project/list.html'


class ProjectCreate(LoginRequiredMixin, CreateView):
    """ View to create a new donation project.
    """
    model = DonationProject
    template_name = 'ddm/research_interface/project/create.html'
    fields = ['name', 'slug']


class ProjectDetail(LoginRequiredMixin, DetailView):
    """ View to display landing page for project.
    """
    model = DonationProject
    template_name = 'ddm/research_interface/project/detail.html'


class ProjectEdit(LoginRequiredMixin, UpdateView):
    """ View to edit the details of an existing donation project.
    """
    model = DonationProject
    template_name = 'ddm/research_interface/project/edit.html'
    fields = ['name', 'slug']


class ProjectDelete(LoginRequiredMixin, DeleteView):
    """ View to display a list of existing donation projects.
    """
    model = DonationProject
    template_name = 'ddm/research_interface/project/delete.html'
    success_url = reverse_lazy('project-list')
