import json

from django.contrib import admin
from django.utils.html import format_html

from ddm.logging.models import ExceptionLogEntry, EventLogEntry


class ExceptionsAdmin(admin.ModelAdmin):
    """
    Provides an overview of all registered exceptions.
    """
    list_display = [
        'formatted_date', 'project', 'participant', 'raised_by',
        'exception_type', 'formatted_message'
    ]
    list_filter = [
        'project', 'exception_type', 'raised_by'
    ]

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='Message')
    def formatted_message(self, obj):
        msg = obj.message
        try:
            msg_json = json.loads(msg)
            msg = json.dumps(msg_json, indent=4, ensure_ascii=False)
            return format_html('<pre>{}</pre>', msg)
        except ValueError:
            msg = msg
        return msg

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
