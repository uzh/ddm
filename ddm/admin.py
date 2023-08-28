from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from ddm.models.core import DonationProject
from ddm.models.logs import ExceptionLogEntry, EventLogEntry


class DonationProjectAdmin(admin.ModelAdmin):
    """
    Provides an overview of all active Donation Projects.
    """
    list_display = ['name', 'owner', 'date_created', 'edit_link']

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Link to Project")
    def edit_link(self, obj):
        url = reverse('project-detail', args=[obj.pk])
        return format_html(f'<a href="{url}">Show Detail Page</a>')


class ExceptionsAdmin(admin.ModelAdmin):
    """
    Provides an overview of all registered exceptions.
    """
    list_display = [
        'formatted_date', 'project', 'raised_by', 'exception_type', 'message'
    ]

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(ordering='date', description='Date')
    def formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d %H:%M:%S')


class EventsAdmin(admin.ModelAdmin):
    """
    Provides an overview of all registered exceptions.
    """
    list_display = ['formatted_date', 'project', 'description', 'message']
    list_filter = ['description']

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(ordering='date', description='Date')
    def formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d %H:%M:%S')


admin.site.register(DonationProject, DonationProjectAdmin)
admin.site.register(ExceptionLogEntry, ExceptionsAdmin)
admin.site.register(EventLogEntry, EventsAdmin)
