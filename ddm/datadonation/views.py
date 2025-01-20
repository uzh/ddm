import io
import json
import zipfile

from django import forms
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.decorators.debug import sensitive_variables
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView

from ddm.apis.serializers import DataDonationSerializer
from ddm.apis.views import DDMAPIMixin
from ddm.datadonation.forms import (
    BlueprintEditForm, ProcessingRuleInlineFormset, SecretInputForm
)
from ddm.datadonation.models import (
    DonationBlueprint, DonationInstruction, FileUploader
)
from ddm.encryption.models import Decryption, Encryption
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.projects.views import DDMAuthMixin


class BlueprintMixin:
    """ Mixin for all blueprint related views. """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_uploaders = FileUploader.objects.filter(project__url_id=self.kwargs['project_url_id'])
        context.update({
            'project': DonationProject.objects.get(url_id=self.kwargs['project_url_id']),
            'file_uploader_meta': {str(fu.pk): fu.upload_type for fu in file_uploaders}
        })
        return context

    def get_success_url(self):
        return reverse(
            'ddm_datadonation:overview',
            kwargs={'project_url_id': self.kwargs['project_url_id']}
        )


class DataDonationOverview(DDMAuthMixin, BlueprintMixin, ListView):
    """ View to list all file uploaders associated with a project. """
    model = FileUploader
    context_object_name = 'file_uploaders'
    template_name = 'ddm_datadonation/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'lonely_blueprints': context['project'].donationblueprint_set.filter(file_uploader=None)})
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(project__url_id=self.kwargs['project_url_id'])
        return queryset


class FileUploaderCreate(SuccessMessageMixin, DDMAuthMixin, BlueprintMixin, CreateView):
    """ View to create a new file uploader. """
    model = FileUploader
    template_name = 'ddm_datadonation/uploader/create.html'
    fields = ['name', 'upload_type', 'combined_consent']
    success_message = 'File Uploader was created successfully.'

    def form_valid(self, form):
        project_url_id = self.kwargs['project_url_id']
        project = DonationProject.objects.get(url_id=project_url_id)
        form.instance.project_id = project.pk
        return super().form_valid(form)

    def get_success_url(self):
        kwargs = {
            'project_url_id': self.kwargs['project_url_id'],
            'pk': self.object.pk
        }
        return reverse('ddm_datadonation:uploaders:edit', kwargs=kwargs)


class FileUploaderEdit(SuccessMessageMixin, DDMAuthMixin, BlueprintMixin, UpdateView):
    """ View to edit the details of an existing file uploader. """
    model = FileUploader
    template_name = 'ddm_datadonation/uploader/edit.html'
    fields = ['name', 'upload_type', 'combined_consent', 'index']
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
            Q(file_uploader=self.object) | Q(file_uploader=None), project__url_id=self.kwargs['project_url_id'])
        return relevant_blueprints

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        selected_blueprints = [int(k[3:]) for k in self.request.POST.keys() if k.startswith('bp-')]
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


class FileUploaderDelete(SuccessMessageMixin, DDMAuthMixin, BlueprintMixin, DeleteView):
    """ View to delete an existing blueprint uploader. """
    model = FileUploader
    template_name = 'ddm_datadonation/uploader/delete.html'
    success_message = 'File Uploader "%s" was deleted.'

    def get_success_message(self, cleaned_data):
        return self.success_message % self.object.name


class BlueprintCreate(SuccessMessageMixin, DDMAuthMixin, BlueprintMixin, CreateView):
    """ View to create a new donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm_datadonation/blueprint/create.html'
    form_class = BlueprintEditForm
    success_message = 'Blueprint was created successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available_file_uploaders = FileUploader.objects.filter(project__url_id=self.kwargs['project_url_id'])
        context['form'].fields['file_uploader'].queryset = available_file_uploaders
        return context

    def form_valid(self, form):
        project_url_id = self.kwargs['project_url_id']
        project = DonationProject.objects.get(url_id=project_url_id)
        form.instance.project_id = project.pk
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ddm_datadonation:blueprints:edit',
                       kwargs={'project_url_id': self.object.project.url_id, 'pk': self.object.pk})


class BlueprintEdit(SuccessMessageMixin, DDMAuthMixin, BlueprintMixin, UpdateView):
    """ View to edit the details of an existing donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm_datadonation/blueprint/edit.html'
    form_class = BlueprintEditForm
    success_message = 'Blueprint "%(name)s" was successfully updated.'

    def get_success_url(self):
        return reverse(
            'ddm_datadonation:overview',
            kwargs={'project_url_id': self.object.project.url_id}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available_file_uploaders = FileUploader.objects.filter(
            project__url_id=self.kwargs['project_url_id'])
        context['form'].fields['file_uploader'].queryset = available_file_uploaders
        context['formset'] = ProcessingRuleInlineFormset(
            instance=self.object, queryset=self.object.processingrule_set.order_by('execution_order'))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
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


class BlueprintDelete(SuccessMessageMixin, DDMAuthMixin, BlueprintMixin, DeleteView):
    """ View to delete an existing donation blueprint. """
    model = DonationBlueprint
    template_name = 'ddm_datadonation/blueprint/delete.html'
    success_message = 'Blueprint "%s" was deleted.'

    def get_success_message(self, cleaned_data):
        return self.success_message % self.object.name


class InstructionMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'project_url_id': self.kwargs['project_url_id']})
        context.update({'file_uploader': FileUploader.objects.get(pk=self.kwargs['file_uploader_pk'])})
        return context

    def get_success_url(self):
        kwargs = {'project_url_id': self.kwargs['project_url_id'],
                  'file_uploader_pk': self.kwargs['file_uploader_pk']}
        return reverse('ddm_datadonation:instructions:overview', kwargs=kwargs)


class InstructionOverview(DDMAuthMixin, InstructionMixin, ListView):
    """ View to create a new instruction page. """
    model = DonationInstruction
    context_object_name = 'instructions'
    template_name = 'ddm_datadonation/instructions/list.html'
    fields = ['text', 'index']

    def get_queryset(self):
        queryset = super().get_queryset().filter(file_uploader_id=self.kwargs['file_uploader_pk'])
        return queryset


class InstructionCreate(SuccessMessageMixin, DDMAuthMixin, InstructionMixin, CreateView):
    """ View to create an instruction page. """
    model = DonationInstruction
    template_name = 'ddm_datadonation/instructions/create.html'
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


class InstructionEdit(SuccessMessageMixin, DDMAuthMixin, InstructionMixin, UpdateView):
    """ View to edit an instruction page. """
    model = DonationInstruction
    template_name = 'ddm_datadonation/instructions/edit.html'
    fields = ['text', 'index']
    success_message = 'Instruction page was successfully updated.'


class InstructionDelete(SuccessMessageMixin, DDMAuthMixin, InstructionMixin, DeleteView):
    """ View to delete an instruction page. """
    model = DonationInstruction
    template_name = 'ddm_datadonation/instructions/delete.html'
    success_message = 'Instruction page was deleted.'

    def get_success_message(self, cleaned_data):
        return self.success_message % self.object.name


class DonationDownloadView(DDMAuthMixin, DDMAPIMixin, FormView):
    """View to download all the donations of one specific participant."""

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project = self.get_project()
        except Http404 as e:
            raise Http404(str(e))
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return SecretInputForm if self.project.super_secret else forms.Form

    def get_template_names(self):
        regular_template = 'ddm_datadonation/download_regular.html'
        secret_template = 'ddm_datadonation/download_with_secret.html'
        return secret_template if self.project.super_secret else regular_template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'project': self.project,
            'participant_id': self.kwargs.get('participant_id'),
        })
        return context

    def get_success_url(self):
        url = reverse_lazy(
            'ddm_datadonation:download_donation',
            kwargs={
                'project_url_id': self.kwargs.get('project_url_id'),
                'participant_id': self.kwargs.get('participant_id')
            })
        return url

    def get_participant(self):
        """ Returns participant instance. """
        participant_id = self.kwargs.get('participant_id')
        return get_object_or_404(Participant, external_id=participant_id)

    def get_donations(self, participant):
        return participant.datadonation_set.all()

    @sensitive_variables()
    def form_valid(self, form):
        try:
            decryptor = self.get_decryptor(form.cleaned_data.get('secret'))
        except ValueError as e:
            form.add_error('secret', 'Incorrect secret.')
            self.create_event_log(
                descr='Donation download failed.',
                msg=f'Download attempt with incorrect secret was registered.'
            )
            return HttpResponse('Incorrect secret', status=422)

        return self.get_data_response(decryptor)

    @sensitive_variables()
    def get_decryptor(self, secret=None):
        secret_key = secret if secret else self.project.secret_key
        decryptor = Decryption(secret_key, self.project.get_salt())
        try:
            self.test_secret(secret_key, decryptor)
        except ValueError:
            raise ValueError
        return decryptor

    @sensitive_variables()
    def test_secret(self, secret, decryptor):
        test_string = 'Teststring'
        encrypted_string = Encryption(public=self.project.public_key).encrypt(test_string)

        try:
            decrypted_string = decryptor.decrypt(encrypted_string)
        except ValueError:
            raise ValueError

        if decrypted_string != test_string:
            raise ValueError

    @staticmethod
    def create_zip(content, participant_id):
        """ Creates a zip file in memory. """
        buffer = io.BytesIO()
        filename = f'ddm_donations_{participant_id}.json'
        with zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            with zf.open(filename, 'w') as json_file:
                json_content = json.dumps(
                    content, ensure_ascii=False, separators=(',', ':'))
                json_file.write(json_content.encode('utf-8'))
                zf.testzip()
        zip_in_memory = buffer.getvalue()
        buffer.flush()
        return zip_in_memory

    @staticmethod
    def create_zip_response(zip_file, participant_id):
        """ Creates an HttpResponse object containing the provided zip file. """
        filename = f'ddm_donations_{participant_id}.zip'
        response = HttpResponse(zip_file, content_type='application/zip')
        response['Content-Length'] = len(zip_file)
        response['Content-Disposition'] = f'attachment; filename={filename}.zip'
        return response

    @sensitive_variables()
    def get_data_response(self, decryptor, *args, **kwargs):
        participant = self.get_participant()
        donations = self.get_donations(participant)

        result = []
        for donation in donations:
            result.append({
                'blueprint': donation.blueprint.pk,
                'donation': DataDonationSerializer(donation, decryptor=decryptor).data,
            })

        zip_in_mem = self.create_zip(result, participant.external_id)
        response = self.create_zip_response(zip_in_mem, participant.external_id)

        self.create_event_log(
            descr='Donation download registered.',
            msg=f'Donation for participant {participant} downloaded.'
        )
        return response
