from ddm.models.core import DonationProject, Participant, DonationBlueprint
from ddm.models.logs import ExceptionLogEntry
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class ExceptionAPI(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None, *args, **kwargs):
        """
        Except an error message and log it
        """
        project_id = self.kwargs['pk']
        project = DonationProject.objects.get(pk=project_id)

        participant_id = request.session['projects'][f'{project_id}']['participant_id']
        participant = Participant.objects.get(pk=participant_id)

        # Get related blueprint
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
