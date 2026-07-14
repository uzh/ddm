from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from ddm.projects.models import DonationProject


@admin.register(DonationProject)
class DonationProjectAdmin(admin.ModelAdmin):
    """
    Provides an overview of all active Donation Projects.
    """

    list_display = ["name", "owner", "date_created", "edit_link"]
    readonly_fields = ["date_created"]

    def has_add_permission(
        self, request: HttpRequest, obj: DonationProject | None = None
    ) -> bool:
        return False

    @admin.display(description="Link to Project")
    def edit_link(self, obj: DonationProject) -> str:
        url = reverse("ddm_projects:detail", args=[obj.url_id])
        # TODO: Check deprecation hint
        return format_html(f'<a href="{url}">Show Detail Page</a>')
