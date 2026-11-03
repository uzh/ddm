import logging
from datetime import datetime

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from ddm.apis.pagination import BootstrapTablePagination
from ddm.apis.permissions import IsProjectOwner
from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.logging.api.filters import EventLogFilter, ExceptionLogFilter
from ddm.logging.api.serializers import (
    EventLogEntrySerializer,
    ExceptionLogBundleSerializer,
    ExceptionLogEntrySerializer,
)
from ddm.logging.models import EventLogEntry, ExceptionLogEntry, ExceptionRaisers
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject

logger = logging.getLogger("ddm")

SESSION_LOST_DESCRIPTION = "Client log received without participant session"

DEFAULT_EXCEPTION_LOG_THROTTLE_RATE = "20/min"


class ExceptionLogThrottle(AnonRateThrottle):
    """Per-IP rate limit for the public, unauthenticated ExceptionAPI.

    Rate is read from DDM_SETTINGS falling back to DEFAULT_EXCEPTION_LOG_THROTTLE_RATE.
    """

    scope = "exception_log"

    def __init__(self) -> None:
        self.rate = getattr(settings, "DDM_SETTINGS", {}).get(
            "EXCEPTION_LOG_THROTTLE_RATE", DEFAULT_EXCEPTION_LOG_THROTTLE_RATE
        )
        self.num_requests, self.duration = self.parse_rate(self.rate)


class ExceptionAPI(APIView):
    """
    Endpoint to post exceptions that occurred in the frontend component and
    create ExceptionLogEntry objects.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ExceptionLogThrottle]

    def post(
        self,
        request: HttpRequest,
        format: str | None = None,  # noqa: A002
        *args,
        **kwargs,
    ) -> Response:
        """
        Log a bundle of exception/stat messages received from the client in
        one request (see useLogPoster.ts: one processing session's logs are
        sent together).
        """
        project_url_id = self.kwargs["project_url_id"]
        project = get_object_or_404(DonationProject, url_id=project_url_id)

        # 404 on an unknown project takes priority over a 400 on a malformed body
        serializer = ExceptionLogBundleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            participant_id = request.session[f"project-{project.pk}"]["participant_id"]
            participant = Participant.objects.get(pk=participant_id)
        except (KeyError, TypeError, ValueError, Participant.DoesNotExist):
            # KeyError: no participation session for this project (cookie not
            # sent, direct/replayed request). TypeError/ValueError: malformed
            # session value. DoesNotExist: the participant has since been
            # deleted (participant FK is SET_NULL, see ExceptionLogEntry).
            participant = None

        raw_date = validated_data.get("date")
        try:
            post_date = parse_datetime(raw_date) if isinstance(raw_date, str) else None
        except ValueError:
            post_date = None
        if post_date is None or timezone.is_naive(post_date):
            # Note: conservative fallback - the current frontend include tz aware date
            post_date = timezone.now()

        # A log bundle typically repeats an uploader and blueprints across
        # many entries, so we cache resolved FKs instead of re-querying per entry.
        uploader_cache: dict[int | None, FileUploader | None] = {}
        blueprint_cache: dict[int | None, DonationBlueprint | None] = {}

        # At most one EventLogEntry is logged per bundle (see
        # log_missing_participant_session), so only the first such entry is kept.
        session_lost_entry_logged: bool = False

        entries = []
        for item in validated_data["logs"]:
            uploader_id = item["uploader"]
            if uploader_id not in uploader_cache:
                uploader_cache[uploader_id] = FileUploader.objects.filter(
                    pk=uploader_id, project=project
                ).first()
            uploader = uploader_cache[uploader_id]

            blueprint_id = item["blueprint"]
            if blueprint_id not in blueprint_cache:
                blueprint_cache[blueprint_id] = DonationBlueprint.objects.filter(
                    pk=blueprint_id, project=project
                ).first()
            blueprint = blueprint_cache[blueprint_id]

            entries.append(
                ExceptionLogEntry(
                    date=post_date,
                    project=project,
                    participant=participant,
                    exception_type=item["status_code"],
                    message=item["message"],
                    raised_by=ExceptionRaisers.CLIENT,
                    blueprint=blueprint,
                    uploader=uploader,
                )
            )

            entry_is_session_lost = participant is None and uploader is not None
            if not session_lost_entry_logged and entry_is_session_lost:
                self.log_missing_participant_session(
                    project,
                    uploader,
                    blueprint,
                    item["status_code"],
                    post_date,
                )
                session_lost_entry_logged = True

        ExceptionLogEntry.objects.bulk_create(entries)

        return Response(None, status=201)

    @staticmethod
    def log_missing_participant_session(
        project: DonationProject,
        uploader: FileUploader | None,
        blueprint: DonationBlueprint | None,
        status_code: str | None,
        post_date: datetime,
    ) -> None:
        """
        Record that a genuine client log (it carries a known uploader) arrived
        without a resolvable participant session, so researchers/ops can estimate
        how often the participant identity is being lost at write time.

        Logged at most once per bundle and request.
        """
        message = (
            f"A client-side '{status_code}' log was received for uploader "
            f"{uploader.pk if uploader else None} "
            f"(blueprint {blueprint.pk if blueprint else None}) "
            f"but no participant could be resolved from the session. The "
            f"participant identity for this log is lost."
        )
        logger.warning("[project %s] %s", project.pk, message)

        already_logged = EventLogEntry.objects.filter(
            project=project,
            description=SESSION_LOST_DESCRIPTION,
            date=post_date,
        ).exists()
        if not already_logged:
            EventLogEntry.objects.create(
                project=project,
                description=SESSION_LOST_DESCRIPTION,
                message=message,
                date=post_date,
            )


class EventLogAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, (IsProjectOwner | IsAdminUser)]

    filterset_class = EventLogFilter
    pagination_class = BootstrapTablePagination
    serializer_class = EventLogEntrySerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = {
        "date": ["icontains", "gte", "lte"],
        "description": ["icontains"],
        "message": ["icontains"],
    }
    ordering_fields = ["date", "description", "message"]
    ordering = ["-date"]
    search_fields = ["description", "message"]

    def get_queryset(self) -> QuerySet[EventLogEntry]:
        project_url_id = self.kwargs["project_url_id"]
        if not DonationProject.objects.filter(url_id=project_url_id).exists():
            msg = "Project not found."
            raise NotFound(msg)
        return EventLogEntry.objects.filter(project__url_id=project_url_id)


class ExceptionLogAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, (IsProjectOwner | IsAdminUser)]

    filterset_class = ExceptionLogFilter
    pagination_class = BootstrapTablePagination
    serializer_class = ExceptionLogEntrySerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = [
        "date",
        "exception_type",
        "raised_by",
        "message",
        "participant__external_id",
        "blueprint__name",
    ]
    ordering = ["-date"]
    search_fields = ["exception_type", "message", "raised_by"]

    def get_queryset(self) -> QuerySet[ExceptionLogEntry]:
        project_url_id = self.kwargs["project_url_id"]
        if not DonationProject.objects.filter(url_id=project_url_id).exists():
            msg = "Project not found."
            raise NotFound(msg)
        return ExceptionLogEntry.objects.filter(
            project__url_id=project_url_id
        ).select_related("participant", "blueprint")
