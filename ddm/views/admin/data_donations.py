from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.forms import BlueprintEditForm, ProcessingRuleInlineFormset
from ddm.models.core import DonationBlueprint, DonationInstruction, DonationProject, FileUploader
from ddm.views.admin import DdmAuthMixin


class BlueprintMixin:
    """ Mixin for all blueprint related views. """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_uploaders = FileUploader.objects.filter(project__pk=self.kwargs['project_pk'])
        context.update({
            'project': DonationProject.objects.get(pk=self.kwargs['project_pk']),
            'file_uploader_meta': {str(fu.pk): fu.upload_type for fu in file_uploaders}
        })
        return context

    def get_success_url(self):
        return reverse('data-donation-overview', kwargs={'project_pk': self.kwargs['project_pk']})


class DataDonationOverview(DdmAuthMixin, BlueprintMixin, ListView):
    """ View to list all file uploaders associated with a project. """
    model = FileUploader
    context_object_name = 'file_uploaders'
    template_name = 'ddm/admin/data_donation/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'lonely_blueprints': context['project'].donationblueprint_set.filter(file_uploader=None)})
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(project_id=self.kwargs['project_pk'])
        return queryset


class FileUploaderCreate(SuccessMessageMixin, DdmAuthMixin, BlueprintMixin, CreateView):
    """ View to create a new file uploader. """
    model = FileUploader
    template_name = 'ddm/admin/data_donation/file_uploader/create.html'
    fields = ['name', 'upload_type']
    success_message = 'File Uploader was created successfully.'

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_pk']
        return super().form_valid(form)

    def get_success_url(self):
        kwargs = {
            'project_pk': self.kwargs['project_pk'],
            'pk': self.object.pk
        }
        return reverse('file-uploader-edit', kwargs=kwargs)


class FileUploaderEdit(SuccessMessageMixin, DdmAuthMixin, BlueprintMixin, UpdateView):
    """ View to edit the details of an existing file uploader. """
    model = FileUploader
    template_name = 'ddm/admin/data_donation/file_uploader/edit.html'
    fields = ['name', 'upload_type', 'index']
    success_message = 'Blueprint Uploader "%(name)s" was successfully updated.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'blueprints': self.get_relevant_blueprints()})
        return context

    def get_relevant_blueprints(self):
        """
        Returns a query set containing all blueprints that are associated with
        the current or no file uploader.
        """
        relevant_blueprints = DonationBlueprint.objects.filter(
            Q(file_uploader=self.object) | Q(file_uploader=None), project__pk=self.kwargs['project_pk'])
        return relevant_blueprints

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # Add custom error.
        selected_blueprints = [int(k[3:]) for k in self.request.POST.keys() if k.startswith('bp-')]
        if form.data['upload_type'] == FileUploader.UploadTypes.SINGLE_FILE:
            if len(selected_blueprints) > 1:
                form.add_error(None, 'Only one Donation Blueprint can be assigned to a single file File Uploader.')

        # Validate form.
        if form.is_valid():
            return self.form_valid(form, selected_blueprints)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, selected_blueprints):
        self.object = form.save()

        # Update file_upload foreign key on donation blueprints.
        relevant_blueprints = self.get_relevant_blueprints()
        for bp in relevant_blueprints:
            if bp.pk in selected_blueprints:
                bp.file_uploader = self.object
                bp.save()
            elif bp.file_uploader == self.object:
                bp.file_uploader = None
                bp.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            self.success_message % dict(name=self.object.name),
            fail_silently=True,
        )
        return HttpResponseRedirect(self.get_success_url())


class FileUploaderDelete(DdmAuthMixin, BlueprintMixin, DeleteView):
    """ View to delete an existing blueprint uploader. """
    model = FileUploader
    template_name = 'ddm/admin/data_donation/file_uploader/delete.html'
    success_message = 'File Uploader "%s" was deleted.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message % self.get_object().name)
        return super().delete(request, *args, **kwargs)


class BlueprintCreate(SuccessMessageMixin, DdmAuthMixin, BlueprintMixin, CreateView):
    """ View to create a new donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm/admin/data_donation/donation_blueprint/create.html'
    form_class = BlueprintEditForm
    success_message = 'Blueprint was created successfully.'

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blueprint-edit', kwargs={'project_pk': self.object.project.pk, 'pk': self.object.pk})


class BlueprintEdit(SuccessMessageMixin, DdmAuthMixin, BlueprintMixin, UpdateView):
    """ View to edit the details of an existing donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm/admin/data_donation/donation_blueprint/edit.html'
    form_class = BlueprintEditForm
    success_message = 'Blueprint "%(name)s" was successfully updated.'

    def get_success_url(self):
        return reverse('data-donation-overview', kwargs={'project_pk': self.object.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available_file_uploaders = FileUploader.objects.filter(project_id=self.kwargs['project_pk'])
        context['form'].fields['file_uploader'].queryset = available_file_uploaders
        context['formset'] = ProcessingRuleInlineFormset(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = ProcessingRuleInlineFormset(self.request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            self.success_message % dict(name=self.object.name),
            fail_silently=True,
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class BlueprintDelete(DdmAuthMixin, BlueprintMixin, DeleteView):
    """ View to delete an existing donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm/admin/data_donation/donation_blueprint/delete.html'
    success_message = 'Blueprint "%s" was deleted.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message % self.get_object().name)
        return super().delete(request, *args, **kwargs)


class InstructionMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'project_pk': self.kwargs['project_pk']})
        context.update({'file_uploader': FileUploader.objects.get(pk=self.kwargs['file_uploader_pk'])})
        return context

    def get_success_url(self):
        kwargs = {'project_pk': self.kwargs['project_pk'],
                  'file_uploader_pk': self.kwargs['file_uploader_pk']}
        return reverse('instruction-overview', kwargs=kwargs)


class InstructionOverview(DdmAuthMixin, InstructionMixin, ListView):
    """ View to create a new instruction page. """
    model = DonationInstruction
    context_object_name = 'instructions'
    template_name = 'ddm/admin/data_donation/instructions/list.html'
    fields = ['text', 'index']

    def get_queryset(self):
        queryset = super().get_queryset().filter(file_uploader_id=self.kwargs['file_uploader_pk'])
        return queryset


class InstructionCreate(SuccessMessageMixin, DdmAuthMixin, InstructionMixin, CreateView):
    """ View to create an instruction page. """
    model = DonationInstruction
    template_name = 'ddm/admin/data_donation/instructions/create.html'
    fields = ['text', 'index']
    success_message = 'Instruction page was successfully created.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = DonationInstruction(file_uploader=FileUploader.objects.get(id=self.kwargs['file_uploader_pk']))
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        related_file_uploader = FileUploader.objects.get(id=self.kwargs['file_uploader_pk'])
        indices = related_file_uploader.donationinstruction_set.values_list('index', flat=True)
        if indices:
            initial['index'] = max(indices) + 1
        else:
            initial['index'] = 1
        return initial


class InstructionEdit(SuccessMessageMixin, DdmAuthMixin, InstructionMixin, UpdateView):
    """ View to edit an instruction page. """
    model = DonationInstruction
    template_name = 'ddm/admin/data_donation/instructions/edit.html'
    fields = ['text', 'index']
    success_message = 'Instruction page was successfully updated.'


class InstructionDelete(DdmAuthMixin, InstructionMixin, DeleteView):
    """ View to delete an instruction page. """
    model = DonationInstruction
    template_name = 'ddm/admin/data_donation/instructions/delete.html'
    success_message = 'Instruction page was deleted.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
