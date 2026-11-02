from rest_framework import serializers

from ddm.logging.models import EventLogEntry, ExceptionLogEntry

# Defense-in-depth cap on how many log entries ExceptionAPI accepts in one
# bundled request. A pathological upload (30 blueprints, each hitting ~5
# distinct processing errors on top of the 3 fixed per-blueprint logs)
# would be ~240; this leaves headroom above that already-generous estimate
# while still rejecting an obviously-abusive request cheaply, before any
# DB work.
MAX_LOGS_PER_REQUEST = 350


class ExceptionLogItemInputSerializer(serializers.Serializer):
    """Validates one entry inside ExceptionAPI's bundled `logs` array.

    Validates that `uploader`/`blueprint` IDs are integers. No validation
    on `status_code`/`message` (deliberately permissive).

    The `raised_by` field is excluded as this serializer is only used to log
    client-side exceptions and is thus hardcoded in the caller.
    """

    status_code = serializers.CharField(allow_blank=True, required=False, default="")
    message = serializers.CharField(allow_blank=True, required=False, default="")
    uploader = serializers.IntegerField(required=False, allow_null=True, default=None)
    blueprint = serializers.IntegerField(required=False, allow_null=True, default=None)


class ExceptionLogBundleSerializer(serializers.Serializer):
    """Validates ExceptionAPI's POST body: one shared batch timestamp plus
    a non-empty list of log entries (see ExceptionLogItemInputSerializer)."""

    date = serializers.CharField(required=False, allow_null=True, default=None)
    logs = ExceptionLogItemInputSerializer(many=True, allow_empty=False)

    def validate_logs(self, value: list) -> list:
        if len(value) > MAX_LOGS_PER_REQUEST:
            msg = f"A single request may contain at most {MAX_LOGS_PER_REQUEST} logs."
            raise serializers.ValidationError(msg)
        return value


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
