from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from ddm.models.core import DonationProject


class DonationProjectAdmin(admin.ModelAdmin):
    """
    Class to hook DDM into admin menu. Redirects to view defined in
    admin_views
    """
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('project-list'))


admin.site.register(DonationProject, DonationProjectAdmin)
