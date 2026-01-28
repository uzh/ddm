from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from ddm.apis.pagination import BootstrapTablePagination
from ddm.apis.permissions import IsProjectOwner
from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.logging.api.filters import EventLogFilter, ExceptionLogFilter
from ddm.logging.models import ExceptionLogEntry, EventLogEntry
from ddm.logging.api.serializers import EventLogEntrySerializer, ExceptionLogEntrySerializer
from ddm.projects.models import DonationProject
from ddm.participation.models import Participant


class ExceptionAPI(APIView):
    """
    Endpoint to post exceptions that occurred in the frontend component and
    create ExceptionLogEntry objects.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None, *args, **kwargs):
        """
        Log exception messages received from client.
        """
        project_url_id = self.kwargs['project_url_id']
        project = DonationProject.objects.get(url_id=project_url_id)

        try:
            participant_id = request.session[f'project-{project.pk}']['participant_id']
            participant = Participant.objects.get(pk=participant_id)
        except KeyError:
            participant = None

        uploader_id = request.data.get('uploader')
        uploader = FileUploader.objects.filter(pk=uploader_id).first()

        blueprint_id = request.data.get('blueprint')
        blueprint = DonationBlueprint.objects.filter(pk=blueprint_id).first()

        if request.data.get('date') is not None:
            post_date = request.data.get('date')
        else:
            post_date = timezone.now()

        ExceptionLogEntry.objects.create(
            date=post_date,
            project=project,
            participant=participant,
            exception_type=request.data.get('status_code'),
            message=request.data.get('message'),
            raised_by=request.data.get('raised_by'),
            blueprint=blueprint,
            uploader=uploader
        )

        return Response(None, status=201)


class EventLogAPIView(ListAPIView):

    permission_classes = [IsAuthenticated, IsProjectOwner, IsAdminUser]

    filterset_class = EventLogFilter
    pagination_class = BootstrapTablePagination
    serializer_class = EventLogEntrySerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = {
        'date': ['icontains', 'gte', 'lte'],
        'description': ['icontains'],
        'message': ['icontains'],
    }
    ordering_fields = ['date', 'description', 'message']
    ordering = ['-date']
    search_fields = ['description', 'message']

    def get_queryset(self):
        project_url_id = self.kwargs['project_url_id']
        return EventLogEntry.objects.filter(project__url_id=project_url_id)


class ExceptionLogAPIView(ListAPIView):

    permission_classes = [IsAuthenticated, IsProjectOwner, IsAdminUser]

    filterset_class = ExceptionLogFilter
    pagination_class = BootstrapTablePagination
    serializer_class = ExceptionLogEntrySerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = [
        'date',
        'exception_type',
        'raised_by',
        'message',
        'participant__external_id',
        'blueprint__name',
    ]
    ordering = ['-date']
    search_fields = ['exception_type', 'message', 'raised_by']

    def get_queryset(self):
        project_url_id = self.kwargs['project_url_id']
        return ExceptionLogEntry.objects.filter(
            project__url_id=project_url_id
        ).select_related('participant', 'blueprint')
