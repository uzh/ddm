from django.core.exceptions import ObjectDoesNotExist

from ddm.models.auth import ProjectTokenAuthenticator
from ddm.models.core import DonationProject, Participant
from ddm.models.logs import EventLogEntry
from ddm.views.download_api import user_is_allowed_to_download

from rest_framework import authentication, exceptions, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response


class ParticipantAPI(APIView):
    """
    Download or delete data collected within a project.

    * Token authentication for remote calls.
    * Session authentication for browser access.
    * Only project owners are able to access this view.
    """
    authentication_classes = [ProjectTokenAuthenticator,
                              authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        Added EventLog entries.
        """
        if request.authenticators and not request.successful_authenticator:
            self.create_event_log(
                descr='Failed participant deletion Attempt',
                msg='Authentication failed.'
            )
            raise exceptions.NotAuthenticated()

        self.create_event_log(
            descr='Failed participant deletion Attempt',
            msg='Permission Denied.'
        )
        raise exceptions.PermissionDenied(detail=message, code=code)

    def get_project(self):
        """ Returns project instance. """
        return DonationProject.objects.filter(pk=self.kwargs['pk']).first()

    def create_event_log(self, descr, msg):
        """ Creates an event log entry related to the current project. """
        return EventLogEntry.objects.create(project=self.get_project(),
                                            description=descr,
                                            message=msg)

    def delete(self, request, format=None, *args, **kwargs):
        """
        Delete participant related to current project by providing external_id.
        """
        project = self.get_project()
        if not user_is_allowed_to_download(request.user, project):
            self.create_event_log(
                descr='Forbidden Deletion Request',
                msg='Request user is not permitted to delete the project data.'
            )
            msg = 'User does not have access.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        external_id = self.kwargs['participant_id']
        try:
            participant = Participant.objects.get(project=project, external_id=external_id)
        except ObjectDoesNotExist:
            msg = f'Participant with id "{external_id}" not found.'
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': msg})

        participant.delete()

        self.create_event_log(
            descr=f'Participant with external id "{external_id}" successfully deleted.',
            msg='Participant deleted.'
        )

        msg = f'Participant with external id "{external_id}" successfully deleted.'
        return Response(status=status.HTTP_200_OK, data={'message': msg})
