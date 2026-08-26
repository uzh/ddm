import json

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView

from ddm.projects.views import DDMAuthMixin
from ddm.questionnaire.models import QuestionBase
from ddm.questionnaire.transfer.forms import QuestionnaireImportUploadForm
from ddm.questionnaire.transfer.services import (
    build_questions,
    copy_question,
    export_questions,
)
from ddm.questionnaire.views import ProjectMixin


class QuestionnaireExportView(ProjectMixin, DDMAuthMixin, View):
    """
    Exports all of a project's questions (+ nested QuestionItem, ScalePoint,
    FilterCondition) as a downloadable JSON file, for import into a
    different project or DDM instance.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        project = self.get_project()
        data = export_questions(project)
        response = HttpResponse(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type="application/json",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{project.slug}-questionnaire-export.json"'
        )
        return response


class QuestionnaireImportView(
    SuccessMessageMixin, ProjectMixin, DDMAuthMixin, FormView
):
    """
    Imports a standalone questionnaire export file into this (existing)
    project. Any question whose blueprint link can't be resolved by name
    in this project is imported unlinked, with a warning shown to the user.
    """

    template_name = "ddm_questionnaire/questionnaire_import.html"
    form_class = QuestionnaireImportUploadForm
    submit_label = "Import Questionnaire"

    def get_breadcrumbs(self) -> list[tuple]:
        crumbs = super().get_breadcrumbs()
        crumbs.append(("Import Questionnaire", None))
        return crumbs

    def form_valid(self, form: QuestionnaireImportUploadForm) -> HttpResponse:
        created, warnings = build_questions(
            form.cleaned_data["file"], self.get_project()
        )
        messages.success(
            self.request, f"Imported {len(created)} question(s) successfully."
        )
        for warning in warnings:
            messages.warning(self.request, warning)
        return redirect(
            "ddm_questionnaire:overview",
            project_url_id=self.kwargs["project_url_id"],
        )


class QuestionCopy(SuccessMessageMixin, DDMAuthMixin, View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest, pk: int, **kwargs) -> HttpResponseRedirect:
        question = get_object_or_404(
            QuestionBase, pk=pk, project__owner__user=request.user
        )
        try:
            new_q = copy_question(question)
        except IntegrityError:
            messages.error(
                request,
                "Couldn't copy the question — please try again.",
            )
            return redirect(self.get_success_url(question))

        messages.success(request, f'Copied as "{new_q.name}".')
        return redirect(self.get_success_url(new_q))

    @staticmethod
    def get_success_url(question: QuestionBase) -> str:
        success_kwargs = {
            "project_url_id": question.project.url_id,
            "question_type": question.question_type,
            "pk": question.pk,
        }
        return reverse("ddm_questionnaire:edit", kwargs=success_kwargs)
