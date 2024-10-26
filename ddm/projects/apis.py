import io
import json
import zipfile

from django.http import HttpResponse
from django.views.decorators.debug import sensitive_variables
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status

from ddm.auth.models import ProjectTokenAuthenticator
from ddm.auth.utils import user_has_project_access
from ddm.core.apis import DDMAPIMixin
from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.datadonation.serializers import DonationSerializer
from ddm.encryption.models import Decryption
from ddm.projects.serializers import ProjectSerializer
from ddm.participation.models import Participant
from ddm.participation.serializers import ParticipantSerializer
from ddm.questionnaire.models import QuestionnaireResponse
from ddm.questionnaire.serializers import ResponseSerializer


class ProjectDataAPI(APIView, DDMAPIMixin):
    """
    Download all data collected for a given donation project.

    Returns:
    - GET: A Response object with the complete data associated to a project (i.e.,
    donated data, questionnaire responses, metadata) and status code.

    Example Usage:
    ```
    GET /api/project/<project_pk>/data

    Returns a ZIP-Folder containing a json file with the following structure:
    {
        'project': {<project information>},
        'donations': {<collected donations per file blueprint>},
        'questionnaire': {<questionnaire responses>}
        'participants': {<participant information>}
    }
    ```

    Authentication Methods:
    - Token authentication for remote calls.
    - Session authentication for access through web application (by verifying
        that the requesting user is the project owner).

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 401 Unauthorized: If authentication fails.
    - 403 Forbidden: If a user is not permitted to access a project (session
        authentication only).
    """
    authentication_classes = [ProjectTokenAuthenticator,
                              authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @sensitive_variables()
    def get(self, request, format=None, *args, **kwargs):
        """
        Return a zip container that contains a json file which holds the
        data donations and questionnaire responses.
        """
        project = self.get_project()
        if not user_has_project_access(request.user, project):
            self.create_event_log(
                descr='Forbidden Download Request',
                msg='Request user is not permitted to download the data.'
            )
            msg = 'User does not have access.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        # Extract secret from request if project is super secret.
        secret = project.secret_key
        if project.super_secret:
            super_secret = None if 'Super-Secret' not in request.headers else request.headers['Super-Secret']
            if super_secret is None:
                self.create_event_log(
                    descr='Failed Download Attempt',
                    msg='Download requested without supplying secret.'
                )
                msg = 'Incorrect key material.'
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'message': msg})
            else:
                secret = super_secret

        # Gather project data in dictionary.
        blueprints = DonationBlueprint.objects.filter(project=project)
        q_responses = QuestionnaireResponse.objects.filter(project=project)
        participants = Participant.objects.filter(project=project)
        try:
            decryptor = Decryption(secret, project.get_salt())

            donations = {}
            for blueprint in blueprints:
                blueprint_donations = blueprint.datadonation_set.all()
                donations[blueprint.name] = [DonationSerializer(d, decryptor=decryptor).data for d in blueprint_donations]

            results = {
                'project': ProjectSerializer(project).data,
                'donations': donations,
                'questionnaire': [ResponseSerializer(r, decryptor=decryptor).data for r in q_responses],
                'participants': [ParticipantSerializer(p).data for p in participants]
            }
        except ValueError:
            self.create_event_log(
                descr='Failed Download Attempt',
                msg='Download requested with incorrect secret.'
            )
            msg = 'Incorrect key material.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        # Create zip file.
        zip_in_mem = self.create_zip(results)
        response = self.create_zip_response(zip_in_mem)
        self.create_event_log(
            descr='Data Download Successful',
            msg='The project data was downloaded.'
        )
        return response

    @staticmethod
    def create_zip(content):
        """ Creates a zip file in memory. """
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            with zf.open('data.json', 'w') as json_file:
                json_file.write(json.dumps(content, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
                zf.testzip()
        zip_in_memory = buffer.getvalue()
        buffer.flush()
        return zip_in_memory

    @staticmethod
    def create_zip_response(zip_file):
        """ Creates an HttpResponse object containing the provided zip file. """
        response = HttpResponse(zip_file, content_type='application/zip')
        response['Content-Length'] = len(zip_file)
        response['Content-Disposition'] = 'attachment; filename=zipfile.zip'
        return response


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
