from ddm.models import DonationProject, ExceptionLogEntry, Participant
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

        ExceptionLogEntry.objects.create(
            date=timezone.now(),
            project=project,
            participant=participant,
            exception_type=request.data['status_code'],
            message=request.data['message']
        )

        return Response(None, status=201)
