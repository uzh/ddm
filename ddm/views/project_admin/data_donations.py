from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.forms import BlueprintEditForm
from ddm.models import DonationBlueprint, ZippedBlueprint, DonationInstruction, DonationProject
from ddm.views.project_admin import DdmAuthMixin


class BlueprintMixin:
    """ Mixin for all blueprint related views. """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'project_pk': self.kwargs['project_pk']})
        context.update({'project': DonationProject.objects.get(pk=self.kwargs['project_pk'])})
        return context

    def get_success_url(self):
        return reverse('blueprint-list', kwargs={'project_pk': self.kwargs['project_pk']})


class ProjectBlueprintList(DdmAuthMixin, BlueprintMixin, ListView):
    """ View to list all donation blueprints associated with a project. """
    model = DonationBlueprint
    context_object_name = 'donation_blueprints'
    template_name = 'ddm/project_admin/blueprint/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'zipped_blueprints': ZippedBlueprint.objects.filter(project_id=self.kwargs['project_pk']),
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(project_id=self.kwargs['project_pk'])
        return queryset


class BlueprintCreate(SuccessMessageMixin, DdmAuthMixin, BlueprintMixin, CreateView):
    """ View to create a new donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm/project_admin/blueprint/create.html'
    fields = ['name', 'exp_file_format', 'expected_fields', 'extracted_fields']
    success_message = 'Blueprint was created successfully.'

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_pk']
        return super().form_valid(form)


class BlueprintEdit(SuccessMessageMixin, DdmAuthMixin, BlueprintMixin, UpdateView):
    """ View to edit the details of an existing donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm/project_admin/blueprint/edit.html'
    form_class = BlueprintEditForm
    success_message = 'Blueprint "%(name)s" was successfully updated.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zbp_queryset = ZippedBlueprint.objects.filter(project_id=self.kwargs['project_pk'])
        context['form'].fields['zip_blueprint'].queryset = zbp_queryset
        return context


class BlueprintDelete(DdmAuthMixin, BlueprintMixin, DeleteView):
    """ View to delete an existing donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm/project_admin/blueprint/delete.html'
    success_message = 'Blueprint "%s" was deleted.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message % self.get_object().name)
        return super().delete(request, *args, **kwargs)


class ZippedBlueprintCreate(SuccessMessageMixin, DdmAuthMixin, BlueprintMixin, CreateView):
    """ View to create a new zipped blueprint. """
    model = ZippedBlueprint
    template_name = 'ddm/project_admin/blueprint/create.html'
    fields = ['name']
    success_message = 'Zip Blueprint was created successfully.'

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_pk']
        return super().form_valid(form)


class ZippedBlueprintEdit(SuccessMessageMixin, DdmAuthMixin, BlueprintMixin, UpdateView):
    """ View to edit the details of an existing zipped blueprint. """
    model = ZippedBlueprint
    template_name = 'ddm/project_admin/blueprint/edit.html'
    fields = ['name']
    success_message = 'Zip blueprint "%(name)s" was successfully updated.'


class ZippedBlueprintDelete(DdmAuthMixin, BlueprintMixin, DeleteView):
    """ View to delete an existing zipped blueprint. """
    model = ZippedBlueprint
    template_name = 'ddm/project_admin/blueprint/delete.html'
    success_message = 'Zip blueprint "%s" was deleted.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message % self.get_object().name)
        return super().delete(request, *args, **kwargs)


class InstructionMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'project_pk': self.kwargs['project_pk']})
        context.update({'project': DonationProject.objects.get(pk=self.kwargs['project_pk'])})
        if self.kwargs['blueprint_type'] == 'blueprint':
            blueprint = DonationBlueprint.objects.get(id=self.kwargs['blueprint_pk'])
            blueprint_type = 'blueprint'
        elif self.kwargs['blueprint_type'] == 'zip-blueprint':
            blueprint = ZippedBlueprint.objects.get(id=self.kwargs['blueprint_pk'])
            blueprint_type = 'zipped Blueprint'
        else:
            raise Http404
        context.update({
            'blueprint': blueprint,
            'blueprint_type': blueprint_type,
        })
        return context

    def get_success_url(self):
        kwargs = {'project_pk': self.kwargs['project_pk'],
                  'blueprint_type': self.kwargs['blueprint_type'],
                  'blueprint_pk': self.kwargs['blueprint_pk']}
        return reverse('instruction-overview', kwargs=kwargs)


class InstructionOverview(DdmAuthMixin, InstructionMixin, ListView):
    """ View to create a new instruction page. """
    model = DonationInstruction
    context_object_name = 'instructions'
    template_name = 'ddm/project_admin/instructions/list.html'
    fields = ['text', 'index']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.kwargs['blueprint_type'] == 'blueprint':
            queryset = queryset.filter(blueprint_id=self.kwargs['blueprint_pk'])
        elif self.kwargs['blueprint_type'] == 'zip-blueprint':
            queryset = queryset.filter(zip_blueprint_id=self.kwargs['blueprint_pk'])
        else:
            raise Http404
        return queryset


class InstructionCreate(SuccessMessageMixin, DdmAuthMixin, InstructionMixin, CreateView):
    """ View to create an instruction page. """
    model = DonationInstruction
    template_name = 'ddm/project_admin/instructions/create.html'
    fields = ['text', 'index']
    success_message = 'Instruction page was successfully created.'

    def get_blueprint(self):
        if self.kwargs['blueprint_type'] == 'blueprint':
            blueprint = DonationBlueprint.objects.get(id=self.kwargs['blueprint_pk'])
        elif self.kwargs['blueprint_type'] == 'zip-blueprint':
            blueprint = ZippedBlueprint.objects.get(id=self.kwargs['blueprint_pk'])
        return blueprint

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        blueprint = self.get_blueprint()
        if isinstance(blueprint, DonationBlueprint):
            kwargs['instance'] = DonationInstruction(blueprint=blueprint)
        elif isinstance(blueprint, ZippedBlueprint):
            kwargs['instance'] = DonationInstruction(zip_blueprint=blueprint)
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        indices = self.get_blueprint().donationinstruction_set.values_list('index', flat=True)
        if indices:
            initial['index'] = max(indices) + 1
        else:
            initial['index'] = 1
        return initial


class InstructionEdit(SuccessMessageMixin, DdmAuthMixin, InstructionMixin, UpdateView):
    """ View to edit an instruction page. """
    model = DonationInstruction
    template_name = 'ddm/project_admin/instructions/edit.html'
    fields = ['text', 'index']
    success_message = 'Instruction page was successfully updated.'


class InstructionDelete(DdmAuthMixin, InstructionMixin, DeleteView):
    """ View to delete an instruction page. """
    model = DonationInstruction
    template_name = 'ddm/project_admin/instructions/delete.html'
    success_message = 'Instruction page was deleted.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        kwargs = {'project_pk': self.kwargs['project_pk'],
                  'blueprint_type': self.kwargs['blueprint_type'],
                  'blueprint_pk': self.kwargs['blueprint_pk']}
        return reverse('instruction-overview', kwargs=kwargs)
