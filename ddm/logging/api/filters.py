import django_filters

from ddm.logging.models import EventLogEntry, ExceptionLogEntry


class EventLogFilter(django_filters.FilterSet):
    date = django_filters.CharFilter(field_name="date", lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    message = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = EventLogEntry
        fields = ["date", "description", "message"]


class ExceptionLogFilter(django_filters.FilterSet):
    date = django_filters.CharFilter(field_name="date", lookup_expr="icontains")
    participant = django_filters.CharFilter(
        field_name="participant__external_id", lookup_expr="icontains"
    )
    exception_type = django_filters.CharFilter(lookup_expr="icontains")
    raised_by = django_filters.CharFilter(lookup_expr="icontains")
    blueprint = django_filters.CharFilter(
        field_name="blueprint__name", lookup_expr="icontains"
    )
    message = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = ExceptionLogEntry
        fields = [
            "date",
            "participant",
            "exception_type",
            "raised_by",
            "blueprint",
            "message",
        ]
