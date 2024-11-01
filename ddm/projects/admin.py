from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from ddm.projects.models import DonationProject


class DonationProjectAdmin(admin.ModelAdmin):
    """
    Provides an overview of all active Donation Projects.
    """
    list_display = ['name', 'owner', 'date_created', 'edit_link']
    readonly_fields = ['date_created']

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Link to Project")
    def edit_link(self, obj):
        url = reverse('ddm_projects:detail', args=[obj.pk])
        return format_html(f'<a href="{url}">Show Detail Page</a>')


admin.site.register(DonationProject, DonationProjectAdmin)
