from typing import Any

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.utils.text import Truncator
from django.views.generic import TemplateView

from ddm.auth.views import DDMAuthMixin
from ddm.core.view_mixins import DDMContextMixin
from ddm.logging.models import ExceptionLogEntry
from ddm.projects.models import DonationProject


class EventLogsListView(
    SuccessMessageMixin, DDMContextMixin, DDMAuthMixin, TemplateView
):
    project: DonationProject | None = None
    template_name = "ddm_logging/event_log_list.html"

    def get_breadcrumbs(self) -> list[tuple]:
        project = self.get_project()
        name = Truncator(project.name).chars(15)
        return [
            ("Projects", reverse_lazy("ddm_projects:list")),
            (
                f"{name}",
                reverse(
                    "ddm_projects:detail", kwargs={"project_url_id": project.url_id}
                ),
            ),
            ("Logs", None),
        ]

    def get_project(self) -> DonationProject | None:
        if self.project is None:
            project_url_id = self.kwargs.get("project_url_id")
            project = DonationProject.objects.filter(url_id=project_url_id).first()
            self.project = project
        return self.project

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "project": self.get_project(),
            }
        )
        return context


class ExceptionLogsListView(
    SuccessMessageMixin, DDMContextMixin, DDMAuthMixin, TemplateView
):
    project: DonationProject | None = None
    template_name = "ddm_logging/exception_log_list.html"

    def get_breadcrumbs(self) -> list[tuple]:
        project = self.get_project()
        name = Truncator(project.name).chars(15)
        return [
            ("Projects", reverse_lazy("ddm_projects:list")),
            (
                f"{name}",
                reverse(
                    "ddm_projects:detail", kwargs={"project_url_id": project.url_id}
                ),
            ),
            ("Logs", None),
        ]

    def get_project(self) -> DonationProject | None:
        if self.project is None:
            project_url_id = self.kwargs.get("project_url_id")
            self.project = DonationProject.objects.filter(url_id=project_url_id).first()
        return self.project

    @staticmethod
    def sort_select_options(options: list | set) -> list:
        options_list = [str(e) for e in list(options) if e is not None]
        options_list.sort()
        return options_list

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        qs = ExceptionLogEntry.objects.filter(project=project)

        types = set(qs.values_list("exception_type", flat=True))
        raised_by = set(qs.values_list("raised_by", flat=True))
        blueprints = set(qs.values_list("blueprint__name", flat=True))

        context.update(
            {
                "types_select": self.sort_select_options(types),
                "raised_by_select": self.sort_select_options(raised_by),
                "blueprints_select": self.sort_select_options(blueprints),
                "project": self.get_project(),
            }
        )
        return context
