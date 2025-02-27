from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from ddm.datadonation.models import DonationBlueprint
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

        blueprint_id = request.data.get('blueprint')
        if blueprint_id:
            blueprint = DonationBlueprint.objects.get(pk=blueprint_id)
        else:
            blueprint = None

        ExceptionLogEntry.objects.create(
            project=project,
            participant=participant,
            exception_type=request.data.get('status_code'),
            message=request.data['message'],
            raised_by=request.data.get('raised_by'),
            blueprint=blueprint
        )

        return Response(None, status=201)
