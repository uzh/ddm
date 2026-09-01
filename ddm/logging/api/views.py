import logging
from datetime import datetime

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
from rest_framework.views import APIView

from ddm.apis.pagination import BootstrapTablePagination
from ddm.apis.permissions import IsProjectOwner
from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.logging.api.filters import EventLogFilter, ExceptionLogFilter
from ddm.logging.api.serializers import (
    EventLogEntrySerializer,
    ExceptionLogEntrySerializer,
)
from ddm.logging.models import EventLogEntry, ExceptionLogEntry
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject

logger = logging.getLogger("ddm")

SESSION_LOST_DESCRIPTION = "Client log received without participant session"


class ExceptionAPI(APIView):
    """
    Endpoint to post exceptions that occurred in the frontend component and
    create ExceptionLogEntry objects.
    """

    permission_classes = [permissions.AllowAny]

    def post(
        self,
        request: HttpRequest,
        format: str | None = None,  # noqa: A002
        *args,
        **kwargs,
    ) -> Response:
        """
        Log exception messages received from client.
        """
        project_url_id = self.kwargs["project_url_id"]
        project = get_object_or_404(DonationProject, url_id=project_url_id)

        try:
            participant_id = request.session[f"project-{project.pk}"]["participant_id"]
            participant = Participant.objects.get(pk=participant_id)
        except (KeyError, TypeError, ValueError, Participant.DoesNotExist):
            # KeyError: no participation session for this project (cookie not
            # sent, direct/replayed request). TypeError/ValueError: malformed
            # session value. DoesNotExist: the participant has since been
            # deleted (participant FK is SET_NULL, see ExceptionLogEntry).
            participant = None

        uploader_id = request.data.get("uploader")
        uploader = FileUploader.objects.filter(pk=uploader_id).first()

        blueprint_id = request.data.get("blueprint")
        blueprint = DonationBlueprint.objects.filter(pk=blueprint_id).first()

        raw_date = request.data.get("date")
        try:
            post_date = parse_datetime(raw_date) if isinstance(raw_date, str) else None
        except ValueError:
            post_date = None
        if post_date is None:
            post_date = timezone.now()

        ExceptionLogEntry.objects.create(
            date=post_date,
            project=project,
            participant=participant,
            exception_type=request.data.get("status_code"),
            message=request.data.get("message"),
            raised_by=request.data.get("raised_by"),
            blueprint=blueprint,
            uploader=uploader,
        )

        session_lost = (
            participant is None
            and uploader is not None
            and uploader.project_id == project.pk
        )
        if session_lost:
            self.log_missing_participant_session(
                project, uploader, blueprint, request.data.get("status_code"), post_date
            )

        return Response(None, status=201)

    @staticmethod
    def log_missing_participant_session(
        project: DonationProject,
        uploader: FileUploader,
        blueprint: DonationBlueprint | None,
        status_code: str | None,
        post_date: datetime,
    ) -> None:
        """
        Record that a genuine client log (it carries a known uploader) arrived
        without a resolvable participant session, so researchers/ops can estimate
        how often the participant identity is being lost at write time.

        Deduplicated per processing batch: the frontend stamps every log in one
        batch with the same ``date`` (see useLogPoster), so only the first log
        of a batch creates an EventLogEntry.
        """
        message = (
            f"A client-side '{status_code}' log was received for uploader "
            f"{uploader.pk} (blueprint {blueprint.pk if blueprint else None}) "
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
