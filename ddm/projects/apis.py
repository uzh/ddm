from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status

from ddm.auth.utils import user_has_project_access
from ddm.apis.views import DDMAPIMixin
from ddm.datadonation.models import DataDonation
from ddm.participation.models import Participant
from ddm.questionnaire.models import QuestionnaireResponse


class DeleteProjectData(APIView, DDMAPIMixin):
    """
    Delete all data (i.e., data donations and questionnaire responses)
    collected for a given donation project.

    Returns:
    - A Response object with the status code.

    Example Usage:
    ```
    DELETE /api/project/<project_pk>/data/delete
    {
        'status': '200',
        'data': {'message': 'Deleted <n donations> data donations and
                            <n responses> questionnaire responses.'}
    }
    ```

    Authentication Methods:
    - Session authentication for access through web application (by verifying
        that the requesting user is the project owner).

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 401 Unauthorized: If authentication fails.
    - 403 Forbidden: If a user is not permitted to access a project.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, format=None, *args, **kwargs):
        """
        Delete data donations and questionnaire requests associated with project.
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

        # Delete all related objects.
        Participant.objects.filter(project=project).delete()
        n_deleted_donations = DataDonation.objects.filter(project=project).delete()[0]
        n_deleted_responses = QuestionnaireResponse.objects.filter(project=project).delete()[0]

        self.create_event_log(
            descr='Data Deletion Successful',
            msg='The project data was deleted.'
        )

        msg = (f'Deleted {n_deleted_donations} data donations and '
               f'{n_deleted_responses} questionnaire responses.')
        return Response(status=status.HTTP_200_OK, data={'message': msg})
