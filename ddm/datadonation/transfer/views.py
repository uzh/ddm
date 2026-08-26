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

from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.datadonation.transfer.forms import BlueprintImportUploadForm
from ddm.datadonation.transfer.services import (
    build_blueprint,
    copy_blueprint,
    export_blueprint,
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
        response["Content-Disposition"] = (
            f'attachment; filename="{blueprint.name}-blueprint-export.json"'
        )
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
