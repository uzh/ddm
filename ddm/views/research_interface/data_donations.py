from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.models import DonationBlueprint, ZippedBlueprint


class BlueprintList(LoginRequiredMixin, ListView):
    """ View to display a list of donation blueprints associated with a project.
    """
    model = DonationBlueprint
    template_name = 'ddm/research_interface/blueprint/list.html'


class BlueprintCreate(LoginRequiredMixin, CreateView):
    """ View to create a new donation blueprint for a project.
    """
    model = DonationBlueprint
    template_name = 'ddm/research_interface/blueprint/create.html'
    fields = ['name', 'slug']


class BlueprintDetail(LoginRequiredMixin, DetailView):
    """ View to display the configuration of a donation blueprint.
    """
    model = DonationBlueprint
    template_name = 'ddm/research_interface/blueprint/detail.html'


class BlueprintEdit(LoginRequiredMixin, UpdateView):
    """ View to edit the details of a donation blueprint.
    """
    model = DonationBlueprint
    template_name = 'ddm/research_interface/blueprint/edit.html'
    fields = ['name', 'slug']


class BlueprintDelete(LoginRequiredMixin, DeleteView):
    """ View to display a list of existing donation projects.
    """
    model = DonationBlueprint
    template_name = 'ddm/research_interface/blueprint/delete.html'
    success_url = reverse_lazy('project-list')
