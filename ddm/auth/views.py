from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.utils.text import Truncator
from django.views.generic import FormView
from django.views.generic.base import TemplateView

from ddm.auth.forms import TokenCreationForm
from ddm.auth.models import ProjectAccessToken
from ddm.auth.utils import user_has_project_access, user_is_permitted
from ddm.core.view_mixins import DDMContextMixin
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class DDMAuthMixin:
    """
    Mixin for Class Based Views that handles redirects as follows:
    - unauthenticated users => login page.
    - users without research profiles => create research profile.
    - users without authorization (e.g., due to e-mail restriction)
       => no permission page.
    - users without owner-rights => 404.
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        if request.method in ["GET", "POST"]:
            if not request.user.is_authenticated:
                return redirect("ddm_login")

            if not ResearchProfile.objects.filter(user=request.user).exists():
                ResearchProfile.objects.create(user=request.user)

            if not user_is_permitted(request.user):
                return redirect("ddm_auth:no_permission")

            if request.path not in [
                reverse("ddm_projects:list"),
                reverse("ddm_projects:create"),
                reverse("ddm_projects:import"),
            ]:
                if "project_url_id" in self.kwargs:
                    project_id = self.kwargs["project_url_id"]
                else:
                    raise Http404

                try:
                    project = DonationProject.objects.get(url_id=project_id)
                except DonationProject.DoesNotExist as e:
                    raise Http404 from e

                if (
                    not user_has_project_access(request.user, project)
                    and not request.user.is_superuser
                ):
                    raise Http404
        return super().dispatch(request, *args, **kwargs)


class DdmNoPermissionView(TemplateView):
    """
    View to inform users that they do not have the needed permission rights.
    Implements the following redirects:
    * Unauthenticated users are redirected to the login page.
    * Logged-in users with permission and a research profile are redirected
        to the project list.
    """

    template_name = "ddm_auth/no_permission.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        if request.method == "GET":
            if not request.user.is_authenticated:
                return redirect("ddm_login")
            if (
                user_is_permitted(request.user)
                and ResearchProfile.objects.filter(user=request.user).exists()
            ):
                return redirect("ddm_projects:list")
        return super().dispatch(request, *args, **kwargs)


class ProjectTokenView(SuccessMessageMixin, DDMContextMixin, DDMAuthMixin, FormView):
    """View to see existing access token or generate a new one."""

    template_name = "ddm_auth/token_management.html"
    form_class = TokenCreationForm

    def get_breadcrumbs(self) -> list[tuple[str, str | None]]:
        project = self.get_project()
        name = Truncator(project.name).chars(15)
        project_detail_url = reverse(
            "ddm_projects:detail", kwargs={"project_url_id": project.url_id}
        )
        return [
            ("Projects", reverse_lazy("ddm_projects:list")),
            (f"{name}", project_detail_url),
            ("Manage Access Token", None),
        ]

    def get_project(self) -> DonationProject | None:
        """Returns current project."""
        project_url_id = self.kwargs.get("project_url_id")
        return DonationProject.objects.filter(url_id=project_url_id).first()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context.update(
            {
                "project": project,
                "token": ProjectAccessToken.objects.filter(project=project).first(),
            }
        )
        return context

    def form_valid(self, form: TokenCreationForm) -> HttpResponse:
        """If form is valid, either create new token or delete existing one."""
        project = self.get_project()
        action = form.cleaned_data["action"]

        if action == "create":
            project.create_token(expiration_days=form.cleaned_data["expiration_days"])

        if action == "delete":
            token = project.get_token()
            if token:
                token.delete()

        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            "ddm_auth:project_token",
            kwargs={"project_url_id": self.kwargs.get("project_url_id")},
        )
