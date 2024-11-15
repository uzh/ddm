from django.contrib import admin
from ddm.logging.models import ExceptionLogEntry, EventLogEntry


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


admin.site.register(ExceptionLogEntry, ExceptionsAdmin)
admin.site.register(EventLogEntry, EventsAdmin)
