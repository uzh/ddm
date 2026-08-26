import json
from typing import Any

from django.contrib import messages
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.text import Truncator
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

from ddm.auth.views import DDMAuthMixin
from ddm.core.view_mixins import DDMContextMixin
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.projects.service import suggest_unique_project_slug
from ddm.projects.transfer import build_project, export_project, forms
from ddm.projects.views import BaseProjectMixin

IMPORT_SESSION_KEY = "ddm_project_import_payload"


class ProjectExportView(DDMAuthMixin, DetailView):
    """
    Exports a DonationProject's configuration (file uploaders, blueprints
    and their nested extraction config, and the full questionnaire) as a
    downloadable JSON file. Collected/participant data is never included.
    """

    model = DonationProject
    slug_url_kwarg = "project_url_id"
    slug_field = "url_id"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        project = self.get_object()
        data = export_project(project)
        response = HttpResponse(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{project.slug}-export.json"'
        )
        return response


class ProjectCopyView(BaseProjectMixin, FormView):
    """
    Duplicates an existing project (+ everything nested under it) into a
    brand-new project, in memory (no file round-trip) - the in-app
    counterpart to project export/import. Any owner can copy their own
    project; superusers can additionally pick a different target owner.
    """

    template_name = "ddm_projects/project_copy.html"
    form_class = forms.ProjectNameSlugReviewForm
    submit_label = "Create Copy"

    def get_source_project(self) -> DonationProject:
        return get_object_or_404(DonationProject, url_id=self.kwargs["project_url_id"])

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["include_owner_field"] = self.request.user.is_superuser
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        source = self.get_source_project()
        initial["name"] = f"{source.name} (copy)"
        initial["slug"] = suggest_unique_project_slug(f"{source.slug}-copy")
        if self.request.user.is_superuser:
            initial["owner"] = source.owner
        return initial

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["source_project"] = self.get_source_project()
        return context

    def get_breadcrumbs(self) -> list[tuple]:
        source = self.get_source_project()
        return [
            ("Projects", reverse_lazy("ddm_projects:list")),
            (
                Truncator(source.name).chars(15),
                reverse("ddm_projects:detail", args=[source.url_id]),
            ),
            ("Copy Project", None),
        ]

    def form_valid(self, form: forms.ProjectNameSlugReviewForm) -> HttpResponse:
        source = self.get_source_project()
        owner = form.cleaned_data.get("owner") or ResearchProfile.objects.get(
            user=self.request.user
        )
        payload = export_project(source)
        new_project, warnings = build_project(
            payload,
            owner=owner,
            name=form.cleaned_data["name"],
            slug=form.cleaned_data["slug"],
        )
        messages.success(
            self.request, f'Project "{new_project.name}" was created successfully.'
        )
        for warning in warnings:
            messages.warning(self.request, warning)
        return redirect("ddm_projects:detail", project_url_id=new_project.url_id)


class ProjectImportView(DDMContextMixin, DDMAuthMixin, FormView):
    """
    Imports a project export JSON file to create a brand-new project. Two
    steps in one view (upload, then review the suggested name/slug) tied
    together via a Post/Redirect/Get: step 1's validated payload is stashed
    in the session until step 2 submits or the session expires.
    """

    template_name = "ddm_projects/project_import.html"
    submit_label = "Import Project"

    def get_step(self) -> str:
        return "review" if IMPORT_SESSION_KEY in self.request.session else "upload"

    def get_form_class(self) -> type[Form]:
        if self.get_step() == "review":
            return forms.ProjectNameSlugReviewForm
        return forms.ProjectImportUploadForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.get_step() == "review":
            kwargs["include_owner_field"] = self.request.user.is_superuser
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        if self.get_step() == "review":
            payload = self.request.session[IMPORT_SESSION_KEY]
            source_name = payload.get("project", {}).get("name") or "Imported Project"
            initial["name"] = f"{source_name} (import)"
            initial["slug"] = suggest_unique_project_slug(f"{source_name}-import")
            if self.request.user.is_superuser:
                initial["owner"] = ResearchProfile.objects.filter(
                    user=self.request.user
                ).first()
        return initial

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["step"] = self.get_step()
        return context

    def get_breadcrumbs(self) -> list[tuple]:
        return [
            ("Projects", reverse_lazy("ddm_projects:list")),
            ("Import Project", None),
        ]

    def form_valid(self, form) -> HttpResponse:  # noqa: ANN001
        if self.get_step() == "upload":
            self.request.session[IMPORT_SESSION_KEY] = form.cleaned_data["file"]
            return redirect("ddm_projects:import")

        payload = self.request.session.pop(IMPORT_SESSION_KEY, None)
        if payload is None:
            messages.error(
                self.request,
                "Your import session expired; please upload the file again.",
            )
            return redirect("ddm_projects:import")

        owner = form.cleaned_data.get("owner") or ResearchProfile.objects.get(
            user=self.request.user
        )
        new_project, warnings = build_project(
            payload,
            owner=owner,
            name=form.cleaned_data["name"],
            slug=form.cleaned_data["slug"],
        )
        messages.success(
            self.request, f'Project "{new_project.name}" imported successfully.'
        )
        for warning in warnings:
            messages.warning(self.request, warning)
        return redirect("ddm_projects:detail", project_url_id=new_project.url_id)
