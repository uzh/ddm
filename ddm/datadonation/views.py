import io
import json
import zipfile
from typing import Any

from django import forms
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Q, QuerySet
from django.forms import BaseInlineFormSet, Form
from django.forms.utils import ErrorList
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.text import Truncator
from django.views.decorators.debug import sensitive_variables
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView

from ddm.apis.serializers import DataDonationSerializer
from ddm.apis.views import DDMAPIMixin
from ddm.core.view_mixins import DDMContextMixin
from ddm.datadonation.forms import (
    BlueprintFilePathInlineFormset,
    BlueprintForm,
    FileUploaderForm,
    InstructionsForm,
    ProcessingRuleInlineFormset,
    SecretInputForm,
)
from ddm.datadonation.models import (
    BlueprintFilePath,
    DataDonation,
    DonationBlueprint,
    DonationInstruction,
    FileUploader,
)
from ddm.encryption.models import Decryption, Encryption
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.projects.views import DDMAuthMixin


class DDMAdminMixin(DDMContextMixin):
    """Mixin for admin views providing extra context and utility functions."""

    def get_breadcrumbs(self) -> list[tuple]:
        project = self.get_project()
        name = Truncator(project.name).chars(15)
        return [
            ("Projects", reverse_lazy("ddm_projects:list")),
            (
                f"{name}",
                reverse(
                    "ddm_projects:detail",
                    kwargs={"project_url_id": self.get_project_url_id()},
                ),
            ),
        ]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        url_id = self.get_project_url_id()
        uploaders = FileUploader.objects.filter(project__url_id=url_id)
        uploader_meta_data = {str(fu.pk): fu.upload_type for fu in uploaders}

        context.update(
            {
                "project": DonationProject.objects.get(url_id=url_id),
                "file_uploader_meta": uploader_meta_data,
            }
        )
        return context

    def get_project_url_id(self) -> str:
        return self.kwargs["project_url_id"]

    def get_project(self) -> DonationProject:
        if not hasattr(self, "_project"):
            self._project = DonationProject.objects.get(
                url_id=self.get_project_url_id()
            )
        return self._project

    def get_success_url(self) -> str:
        """Default success url."""
        return reverse(
            "ddm_datadonation:overview",
            kwargs={"project_url_id": self.get_project_url_id()},
        )


class DataDonationOverview(DDMAuthMixin, DDMAdminMixin, ListView):
    """View to list all file uploaders associated with a project."""

    model = FileUploader
    context_object_name = "file_uploaders"
    template_name = "ddm_datadonation/overview.html"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(("Data Donation", None))
        return crumbs

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context.update(
            {
                "lonely_blueprints": project.donationblueprint_set.filter(
                    file_uploader=None
                )
            }
        )
        return context

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(project__url_id=self.get_project_url_id())


class FileUploaderCreate(SuccessMessageMixin, DDMAuthMixin, DDMAdminMixin, CreateView):
    """View to create a new file uploader."""

    model = FileUploader
    template_name = "ddm_datadonation/uploader/create.html"
    form_class = FileUploaderForm
    success_message = "Uploader created successfully."

    submit_label = "Create Uploader"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Data Donation",
                reverse(
                    "ddm_datadonation:overview",
                    kwargs={"project_url_id": self.get_project_url_id()},
                ),
            )
        )
        crumbs.append(("Create Uploader", None))
        return crumbs

    def get_initial(self) -> dict[str, Any]:
        """Set initial index value to current maximum plus one."""
        initial = super().get_initial()
        uploaders = FileUploader.objects.filter(
            project__url_id=self.get_project_url_id()
        )

        if uploaders:
            max_index = uploaders.count()
            initial["index"] = max_index + 1
        else:
            initial["index"] = 1

        return initial

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.get_project()
        return kwargs

    def form_valid(self, form: FileUploaderForm) -> HttpResponse:
        project = DonationProject.objects.get(url_id=self.get_project_url_id())
        form.instance.project_id = project.pk
        return super().form_valid(form)

    def get_success_url(self) -> str:
        kwargs = {
            "project_url_id": self.get_project_url_id(),
        }
        return reverse("ddm_datadonation:overview", kwargs=kwargs)


class FileUploaderEdit(SuccessMessageMixin, DDMAuthMixin, DDMAdminMixin, UpdateView):
    """View to edit the details of an existing file uploader."""

    model = FileUploader
    template_name = "ddm_datadonation/uploader/edit.html"
    form_class = FileUploaderForm
    success_message = 'Uploader "%(name)s" successfully updated.'

    submit_label = "Update Uploader"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Data Donation",
                reverse(
                    "ddm_datadonation:overview",
                    kwargs={"project_url_id": self.get_project_url_id()},
                ),
            )
        )
        crumbs.append(("Edit Uploader", None))
        return crumbs

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.get_project()
        return kwargs

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({"blueprints": self.get_relevant_blueprints()})
        return context

    def get_relevant_blueprints(self) -> QuerySet[DonationBlueprint]:
        """
        Returns a query set containing all blueprints that are associated with
        the current or no file uploader.
        """
        return DonationBlueprint.objects.filter(
            Q(file_uploader=self.object) | Q(file_uploader=None),
            project__url_id=self.get_project_url_id(),
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        form = self.get_form()
        selected_blueprints = [
            int(k[3:])
            for k in self.request.POST
            if k.startswith("bp-")
            # TODO: Optimize this static reference
        ]
        if form.is_valid():
            return self.form_valid(form, selected_blueprints)
        return self.form_invalid(form)

    def form_valid(
        self, form: FileUploaderForm, selected_blueprints: list[int]
    ) -> HttpResponseRedirect:
        with transaction.atomic():
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
            self.request,
            messages.SUCCESS,
            self.success_message % {"name": self.object.name},
            fail_silently=True,
        )
        return HttpResponseRedirect(self.get_success_url())


class FileUploaderDelete(SuccessMessageMixin, DDMAuthMixin, DDMAdminMixin, DeleteView):
    """View to delete an existing blueprint uploader."""

    model = FileUploader
    template_name = "ddm_datadonation/uploader/delete.html"
    success_message = 'Uploader "%s" was deleted.'

    submit_label = "Delete Uploader"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Data Donation",
                reverse(
                    "ddm_datadonation:overview",
                    kwargs={"project_url_id": self.get_project_url_id()},
                ),
            )
        )
        crumbs.append(("Delete Uploader", None))
        return crumbs

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["instructions"] = self.object.donationinstruction_set.count()
        context["blueprints"] = self.object.donationblueprint_set.count()
        return context

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % self.object.name


class BlueprintFormMixin(DDMAdminMixin):
    """Mixins bundling common functionality for Blueprint related form views."""

    object: DonationBlueprint

    def get_project(self) -> DonationProject:
        if not hasattr(self, "_project"):
            if hasattr(self, "object") and self.object:
                self._project = self.object.project
            else:
                self._project = DonationProject.objects.get(
                    url_id=self.get_project_url_id()
                )
        return self._project

    def get_file_uploaders(self) -> QuerySet[FileUploader]:
        return FileUploader.objects.filter(project__url_id=self.get_project_url_id())

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.get_project()
        return kwargs

    def get_path_formset(self, data: dict | None = None) -> BaseInlineFormSet:
        if self.object is None:
            queryset = BlueprintFilePath.objects.none()
        else:
            queryset = self.object.blueprintfilepath_set.all()
        return BlueprintFilePathInlineFormset(
            data, instance=self.object, queryset=queryset
        )

    def form_is_missing_file_paths(
        self, form: BlueprintForm, path_formset: BaseInlineFormSet
    ) -> bool:
        has_paths = any(
            f.cleaned_data and not f.cleaned_data.get("DELETE", False)
            for f in path_formset
        )
        file_uploader = form.cleaned_data.get("file_uploader")

        if file_uploader and not has_paths:
            needs_paths = file_uploader.upload_type == FileUploader.UploadTypes.ZIP_FILE
            if needs_paths:
                return True
        return False

    def add_file_path_error(self, path_formset: BaseInlineFormSet) -> None:
        """Add error for missing file paths. Override to change where error appears."""
        path_formset._non_form_errors = ErrorList(  # noqa: SLF001
            ["ZIP file uploaders require at least one file path."]
        )


class BlueprintCreate(
    SuccessMessageMixin, DDMAuthMixin, BlueprintFormMixin, CreateView
):
    """View to create a new donation blueprint."""

    model = DonationBlueprint
    template_name = "ddm_datadonation/blueprint/create.html"
    form_class = BlueprintForm
    success_message = "Blueprint created successfully."

    submit_label = "Create Blueprint"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Data Donation",
                reverse(
                    "ddm_datadonation:overview",
                    kwargs={"project_url_id": self.get_project_url_id()},
                ),
            )
        )
        crumbs.append(("Create Blueprint", None))
        return crumbs

    def get_initial(self) -> dict[str, Any]:
        """Set initial display_position value to current maximum plus one."""
        initial = super().get_initial()
        project_blueprints = DonationBlueprint.objects.filter(
            project__url_id=self.get_project_url_id()
        )

        if project_blueprints:
            max_position = self.get_current_max_position(project_blueprints)
            initial["display_position"] = max_position + 1
        else:
            initial["display_position"] = 1

        return initial

    @staticmethod
    def get_current_max_position(blueprints: QuerySet[DonationBlueprint]) -> int | None:
        return (
            blueprints.order_by("-display_position")
            .values_list("display_position", flat=True)
            .first()
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"].fields["file_uploader"].queryset = self.get_file_uploaders()

        if "path_formset" not in kwargs:
            context["path_formset"] = self.get_path_formset()
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = None

        form = self.get_form()
        path_formset = self.get_path_formset(request.POST)

        if form.is_valid() and path_formset.is_valid():
            if self.form_is_missing_file_paths(form, path_formset):
                self.add_file_path_error(path_formset)
                return self.form_invalid(form, path_formset)
            return self.form_valid(form, path_formset)
        return self.form_invalid(form, path_formset)

    def form_valid(
        self, form: BlueprintForm, path_formset: BaseInlineFormSet
    ) -> HttpResponseRedirect:
        with transaction.atomic():
            form.instance.project = self.get_project()

            self.object = form.save()
            path_formset.instance = self.object
            path_formset.save()

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(
        self, form: BlueprintForm, path_formset: BaseInlineFormSet
    ) -> HttpResponse:
        context = self.get_context_data(
            form=form,
            path_formset=path_formset,
        )
        return self.render_to_response(context)

    def get_success_url(self) -> str:
        kwargs = {"project_url_id": self.object.project.url_id, "pk": self.object.pk}
        return reverse("ddm_datadonation:blueprints:edit", kwargs=kwargs)


class BlueprintEdit(SuccessMessageMixin, DDMAuthMixin, BlueprintFormMixin, UpdateView):
    """View to edit the details of an existing donation blueprint."""

    model = DonationBlueprint
    template_name = "ddm_datadonation/blueprint/edit.html"
    form_class = BlueprintForm
    success_message = 'Blueprint "%(name)s" successfully updated.'

    submit_label = "Update Blueprint"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Data Donation",
                reverse(
                    "ddm_datadonation:overview",
                    kwargs={"project_url_id": self.get_project_url_id()},
                ),
            )
        )
        crumbs.append(("Edit Blueprint", None))
        return crumbs

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"].fields["file_uploader"].queryset = self.get_file_uploaders()

        if "rule_formset" not in kwargs:
            context["rule_formset"] = self.get_rule_formset()

        if "path_formset" not in kwargs:
            context["path_formset"] = self.get_path_formset()

        return context

    def get_rule_formset(self, data: dict | None = None) -> BaseInlineFormSet:
        return ProcessingRuleInlineFormset(
            data,
            instance=self.object,
            queryset=self.object.processingrule_set.order_by("execution_order"),
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        form = self.get_form()
        rule_formset = self.get_rule_formset(self.request.POST)
        path_formset = self.get_path_formset(self.request.POST)

        if form.is_valid() and rule_formset.is_valid() and path_formset.is_valid():
            if self.form_is_missing_file_paths(form, path_formset):
                self.add_file_path_error(path_formset)
                return self.form_invalid(form, rule_formset, path_formset)
            return self.form_valid(form, rule_formset, path_formset)
        return self.form_invalid(form, rule_formset, path_formset)

    def form_valid(
        self,
        form: BlueprintForm,
        rule_formset: BaseInlineFormSet,
        path_formset: BaseInlineFormSet,
    ) -> HttpResponseRedirect:
        with transaction.atomic():
            self.object = form.save()
            rule_formset.instance = self.object
            rule_formset.save()
            path_formset.instance = self.object
            path_formset.save()

        messages.success(
            self.request, self.success_message % {"name": self.object.name}
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(
        self,
        form: BlueprintForm,
        rule_formset: BaseInlineFormSet,
        path_formset: BaseInlineFormSet,
    ) -> HttpResponse:
        context = self.get_context_data(
            form=form,
            rule_formset=rule_formset,
            path_formset=path_formset,
        )
        return self.render_to_response(context)


class BlueprintDelete(SuccessMessageMixin, DDMAuthMixin, DDMAdminMixin, DeleteView):
    """View to delete an existing donation blueprint."""

    model = DonationBlueprint
    template_name = "ddm_datadonation/blueprint/delete.html"
    success_message = 'Blueprint "%s" deleted.'

    submit_label = "Delete Blueprint"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Data Donation",
                reverse(
                    "ddm_datadonation:overview",
                    kwargs={"project_url_id": self.get_project_url_id()},
                ),
            )
        )
        crumbs.append(("Delete Blueprint", None))
        return crumbs

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % self.object.name


class InstructionMixin(DDMContextMixin):
    def get_breadcrumbs(self) -> list[tuple]:
        project = self.get_project()
        uploader = FileUploader.objects.get(pk=self.get_uploader_id())
        project_name = Truncator(project.name).chars(15)
        uploader_name = Truncator(uploader.name).chars(15)

        project_id = self.get_project_url_id()
        uploader_id = self.get_uploader_id()

        return [
            ("Projects", reverse_lazy("ddm_projects:list")),
            (
                f"{project_name}",
                reverse("ddm_projects:detail", kwargs={"project_url_id": project_id}),
            ),
            (
                "Data Donation",
                reverse(
                    "ddm_datadonation:overview", kwargs={"project_url_id": project_id}
                ),
            ),
            (
                f"{uploader_name}",
                reverse(
                    "ddm_datadonation:uploaders:edit",
                    kwargs={"project_url_id": project_id, "pk": uploader_id},
                ),
            ),
        ]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "project_url_id": self.get_project_url_id(),
                "file_uploader": FileUploader.objects.get(pk=self.get_uploader_id()),
                "project": self.get_project(),
            }
        )
        return context

    def get_project(self) -> DonationProject | None:
        try:
            project = DonationProject.objects.get(url_id=self.get_project_url_id())
        except DonationProject.DoesNotExist:
            project = None
        return project

    def get_project_url_id(self) -> str:
        return self.kwargs["project_url_id"]

    def get_uploader_id(self) -> str:
        return self.kwargs["file_uploader_pk"]

    def get_success_url(self) -> str:
        kwargs = {
            "project_url_id": self.get_project_url_id(),
            "file_uploader_pk": self.get_uploader_id(),
        }
        return reverse("ddm_datadonation:instructions:overview", kwargs=kwargs)


class InstructionOverview(DDMAuthMixin, InstructionMixin, ListView):
    """View to create a new instruction page."""

    model = DonationInstruction
    context_object_name = "instructions"
    template_name = "ddm_datadonation/instructions/list.html"
    fields = ["text", "index"]

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(("Instructions", None))
        return crumbs

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(file_uploader_id=self.get_uploader_id())


class InstructionCreate(
    SuccessMessageMixin, DDMAuthMixin, InstructionMixin, CreateView
):
    """View to create an instruction page."""

    model = DonationInstruction
    form_class = InstructionsForm
    template_name = "ddm_datadonation/instructions/create.html"
    success_message = "Instruction page successfully created."

    submit_label = "Create Instruction Page"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Instructions",
                reverse(
                    "ddm_datadonation:instructions:overview",
                    kwargs={
                        "project_url_id": self.get_project_url_id(),
                        "file_uploader_pk": self.get_uploader_id(),
                    },
                ),
            )
        )
        crumbs.append(("Create Instruction Page", None))
        return crumbs

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = DonationInstruction(
            file_uploader=FileUploader.objects.get(id=self.get_uploader_id())
        )
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        related_file_uploader = FileUploader.objects.get(id=self.get_uploader_id())
        indices = related_file_uploader.donationinstruction_set.values_list(
            "index", flat=True
        )
        if indices:
            initial["index"] = max(indices) + 1
        else:
            initial["index"] = 1
        return initial


class InstructionEdit(SuccessMessageMixin, DDMAuthMixin, InstructionMixin, UpdateView):
    """View to edit an instruction page."""

    model = DonationInstruction
    form_class = InstructionsForm
    template_name = "ddm_datadonation/instructions/edit.html"
    success_message = "Instruction page successfully updated."

    submit_label = "Update Instruction Page"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Instructions",
                reverse(
                    "ddm_datadonation:instructions:overview",
                    kwargs={
                        "project_url_id": self.get_project_url_id(),
                        "file_uploader_pk": self.get_uploader_id(),
                    },
                ),
            )
        )
        crumbs.append(("Edit Instruction Page", None))
        return crumbs


class InstructionDelete(
    SuccessMessageMixin, DDMAuthMixin, InstructionMixin, DeleteView
):
    """View to delete an instruction page."""

    model = DonationInstruction
    template_name = "ddm_datadonation/instructions/delete.html"
    success_message = "Instruction page deleted."

    submit_label = "Delete Instruction Page"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(
            (
                "Instructions",
                reverse(
                    "ddm_datadonation:instructions:overview",
                    kwargs={
                        "project_url_id": self.get_project_url_id(),
                        "file_uploader_pk": self.get_uploader_id(),
                    },
                ),
            )
        )
        crumbs.append(("Delete Instruction Page", None))
        return crumbs


class DonationDownloadView(DDMAuthMixin, DDMAdminMixin, DDMAPIMixin, FormView):
    """View to download all the donations of one specific participant."""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        try:
            self.project = self.get_project()
        except Http404:  # noqa: TRY203
            raise
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self) -> type[Form]:
        return SecretInputForm if self.project.super_secret else forms.Form

    def get_template_names(self) -> str:
        regular_template = "ddm_datadonation/download_regular.html"
        secret_template = "ddm_datadonation/download_with_secret.html"  # noqa: S105
        return secret_template if self.project.super_secret else regular_template

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "project": self.project,
                "participant_id": self.kwargs.get("participant_id"),
            }
        )
        return context

    def get_success_url(self) -> str:
        return reverse_lazy(
            "ddm_datadonation:download_donation",
            kwargs={
                "project_url_id": self.kwargs.get("project_url_id"),
                "participant_id": self.kwargs.get("participant_id"),
            },
        )

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(("Download Participant Data", None))
        return crumbs

    def get_participant(self) -> Participant:
        """Returns participant instance."""
        participant_id = self.kwargs.get("participant_id")
        return get_object_or_404(Participant, external_id=participant_id)

    def get_donations(self, participant: Participant) -> QuerySet[DataDonation]:
        return participant.datadonation_set.all()

    @sensitive_variables()
    def form_valid(self, form: Form) -> HttpResponse:
        try:
            decryptor = self.get_decryptor(form.cleaned_data.get("secret"))
        except ValueError:
            form.add_error("secret", "Incorrect secret.")
            self.create_event_log(
                descr="Donation download failed.",
                msg="Download attempt with incorrect secret was registered.",
            )
            return HttpResponse("Incorrect secret", status=422)

        return self.get_data_response(decryptor)

    @sensitive_variables()
    def get_decryptor(self, secret: str | None = None) -> Decryption:
        secret_key = secret if secret else self.project.secret_key
        decryptor = Decryption(secret_key, self.project.get_salt())
        try:
            self.test_secret(secret_key, decryptor)
        except ValueError as e:
            raise ValueError from e
        return decryptor

    @sensitive_variables()
    def test_secret(self, secret: str, decryptor: Decryption) -> None:
        test_string = "Teststring"
        encrypted_string = Encryption(public=self.project.public_key).encrypt(
            test_string
        )

        try:
            decrypted_string = decryptor.decrypt(encrypted_string)
        except ValueError as e:
            raise ValueError from e

        if decrypted_string != test_string:
            raise ValueError

    def get_filename(self, participant_id: str, file_type: str) -> str:
        return f"ddm_{self.project.url_id}_donations_{participant_id}.{file_type}"

    def create_zip(self, content: Any, participant_id: str) -> bytes:  # noqa: ANN401
        """Creates a zip file in memory."""
        buffer = io.BytesIO()
        filename = self.get_filename(participant_id, "json")
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:  # noqa: SIM117
            with zf.open(filename, "w") as json_file:
                json_content = json.dumps(
                    content, ensure_ascii=False, separators=(",", ":")
                )
                json_file.write(json_content.encode("utf-8"))
                zf.testzip()
        zip_in_memory = buffer.getvalue()
        buffer.flush()
        return zip_in_memory

    def create_zip_response(self, zip_file: bytes, participant_id: str) -> HttpResponse:
        """Creates an HttpResponse object containing the provided zip file."""
        filename = self.get_filename(participant_id, "zip")
        response = HttpResponse(zip_file, content_type="application/zip")
        response["Content-Length"] = len(zip_file)
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    @sensitive_variables()
    def get_data_response(self, decryptor: Decryption, *args, **kwargs) -> HttpResponse:
        participant = self.get_participant()
        donations = self.get_donations(participant)

        result = [
            {
                "blueprint_id": donation.blueprint.pk,
                "blueprint_name": donation.blueprint.name,
                "donation": DataDonationSerializer(donation, decryptor=decryptor).data,
            }
            for donation in donations
        ]

        zip_in_mem = self.create_zip(result, participant.external_id)
        response = self.create_zip_response(zip_in_mem, participant.external_id)

        self.create_event_log(
            descr="Donation download registered.",
            msg=f"Donation for participant {participant} downloaded.",
        )
        return response
