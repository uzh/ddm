from django.http import HttpRequest
from django.views import View
from rest_framework.permissions import BasePermission

from ddm.projects.models import DonationProject


class IsProjectOwner(BasePermission):
    """Allows access only to project owners."""

    def has_permission(self, request: HttpRequest, view: View) -> bool:
        project_url_id = view.kwargs["project_url_id"]
        try:
            project = DonationProject.objects.get(url_id=project_url_id)
        except DonationProject.DoesNotExist:
            return False
        return project.owner.user == request.user
