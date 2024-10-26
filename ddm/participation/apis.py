from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status

from ddm.auth.models import ProjectTokenAuthenticator
from ddm.auth.utils import user_has_project_access
from ddm.core.apis import DDMAPIMixin
from ddm.participation.models import Participant


class DeleteParticipantAPI(APIView, DDMAPIMixin):
    """
    Delete a participant of an owned project by providing their external ID.

    * Session authentication for browser access.
    * Only project owners are able to access this view.

    Returns:
    - A Response object with the status code.

    Authentication Methods:
    - Token authentication for remote calls.
    - Session authentication for access through web application (by verifying
        that the requesting user is the project owner).

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 401 Unauthorized: If authentication fails.
    - 403 Forbidden: If a user is not permitted to access a project.
    """
    authentication_classes = [ProjectTokenAuthenticator,
                              authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, format=None, *args, **kwargs):
        """
        Delete participant related to current project by providing external_id.
        """
        project = self.get_project()
        if not user_has_project_access(request.user, project):
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
