from rest_framework import serializers

from ddm.logging.models import EventLogEntry, ExceptionLogEntry


class EventLogEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d, %H:%M")

    class Meta:
        model = EventLogEntry
        fields = ["date", "description", "message"]


class ExceptionLogEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d, %H:%M")
    participant = serializers.CharField(source="participant.external_id", default=None)
    blueprint = serializers.CharField(source="blueprint.name", default=None)

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
