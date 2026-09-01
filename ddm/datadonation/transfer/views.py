import json
from typing import Any

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.edit import FormView

from ddm.core.utils.transfer.id_mapping import LocalIdAllocator
from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.datadonation.transfer.forms import (
    BlueprintImportUploadForm,
    FileUploaderImportUploadForm,
)
from ddm.datadonation.transfer.services import (
    build_blueprint,
    build_file_uploader,
    copy_blueprint,
    export_blueprint,
    export_file_uploader,
    serialize_file_uploader,
)
from ddm.datadonation.views import DDMAdminMixin
from ddm.projects.views import DDMAuthMixin


class BlueprintCopyView(SuccessMessageMixin, DDMAuthMixin, View):
    http_method_names = ["post"]

    def post(
        self, request: HttpRequest, project_url_id: str, pk: int
    ) -> HttpResponseRedirect:
        blueprint = get_object_or_404(
            DonationBlueprint,
            pk=pk,
            project__url_id=project_url_id,
        )
        try:
            new_bp = copy_blueprint(blueprint)
        except IntegrityError:
            messages.error(
                request,
                "Couldn't copy the blueprint — please try again.",
            )
            return redirect(self.get_success_url(blueprint))

        messages.success(request, f'Copied as "{new_bp.name}".')
        return redirect(self.get_success_url(new_bp))

    def get_success_url(self, blueprint: DonationBlueprint) -> str:
        kwargs = {"project_url_id": blueprint.project.url_id, "pk": blueprint.pk}
        return reverse("ddm_datadonation:blueprints:edit", kwargs=kwargs)


class BlueprintExportView(DDMAuthMixin, View):
    """
    Exports a single DonationBlueprint (+ nested BlueprintFilePath,
    ExtractionField, ProcessingRule) as a downloadable JSON file, for
    import into a different project or DDM instance.
    """

    def get(self, request: HttpRequest, project_url_id: str, pk: int) -> HttpResponse:
        blueprint = get_object_or_404(
            DonationBlueprint, pk=pk, project__url_id=project_url_id
        )
        data = export_blueprint(blueprint)
        response = HttpResponse(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )
        filename = f"ddm_blueprint-{''.join(blueprint.name.split())}-export.json"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class BlueprintImportView(SuccessMessageMixin, DDMAuthMixin, DDMAdminMixin, FormView):
    """
    Imports a standalone blueprint export file into this (existing)
    project, optionally attaching it to one of the project's file
    uploaders.
    """

    template_name = "ddm_datadonation/blueprint/import.html"
    form_class = BlueprintImportUploadForm
    submit_label = "Import Blueprint"

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
        crumbs.append(("Import Blueprint", None))
        return crumbs

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["file_uploader_queryset"] = FileUploader.objects.filter(
            project=self.get_project()
        )
        return kwargs

    def form_valid(self, form: BlueprintImportUploadForm) -> HttpResponse:
        new_bp = build_blueprint(
            form.cleaned_data["file"],
            self.get_project(),
            file_uploader=form.cleaned_data.get("file_uploader"),
        )
        messages.success(self.request, f'Blueprint "{new_bp.name}" imported.')
        return redirect(
            "ddm_datadonation:blueprints:edit",
            project_url_id=self.get_project_url_id(),
            pk=new_bp.pk,
        )


class FileUploaderCopyView(SuccessMessageMixin, DDMAuthMixin, View):
    """
    Duplicates a FileUploader (+ its DonationInstructions and every
    currently-attached DonationBlueprint) within the same project. Reuses
    the export/import engine in memory rather than a bespoke deepcopy
    routine: serialize the uploader (with its blueprints bundled), tweak
    the name to signal a copy, and build it straight back into the same
    project.
    """

    http_method_names = ["post"]

    def post(
        self, request: HttpRequest, project_url_id: str, pk: int
    ) -> HttpResponseRedirect:
        uploader = get_object_or_404(
            FileUploader, pk=pk, project__url_id=project_url_id
        )
        payload = serialize_file_uploader(
            uploader, LocalIdAllocator(), include_blueprints=True
        )
        payload["name"] = f"{payload['name']}_copy"
        new_uploader = build_file_uploader(payload, uploader.project)

        messages.success(request, f'Copied as "{new_uploader.name}".')
        return redirect(
            "ddm_datadonation:overview",
            project_url_id=uploader.project.url_id,
        )


class FileUploaderExportView(DDMAuthMixin, View):
    """
    Exports a single FileUploader (+ nested DonationInstructions and every
    currently-attached DonationBlueprint) as a downloadable JSON file, for
    import into a different project or DDM instance.
    """

    def get(self, request: HttpRequest, project_url_id: str, pk: int) -> HttpResponse:
        uploader = get_object_or_404(
            FileUploader, pk=pk, project__url_id=project_url_id
        )
        data = export_file_uploader(uploader)
        response = HttpResponse(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )
        filename = f"ddm_uploader-{''.join(uploader.name.split())}-export.json"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class FileUploaderImportView(
    SuccessMessageMixin, DDMAuthMixin, DDMAdminMixin, FormView
):
    """
    Imports a standalone FileUploader export file into this (existing)
    project, including every blueprint bundled with it.
    """

    template_name = "ddm_datadonation/uploader/import.html"
    form_class = FileUploaderImportUploadForm
    submit_label = "Import File Uploader"

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
        crumbs.append(("Import File Uploader", None))
        return crumbs

    def form_valid(self, form: FileUploaderImportUploadForm) -> HttpResponse:
        new_uploader = build_file_uploader(
            form.cleaned_data["file"], self.get_project()
        )
        messages.success(self.request, f'File Uploader "{new_uploader.name}" imported.')
        return redirect(
            "ddm_datadonation:overview",
            project_url_id=self.get_project_url_id(),
        )
