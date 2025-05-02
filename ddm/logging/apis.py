from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.logging.models import ExceptionLogEntry
from ddm.projects.models import DonationProject
from ddm.participation.models import Participant


class ExceptionAPI(APIView):

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
