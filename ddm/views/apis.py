import io
import json
import zipfile

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.debug import sensitive_variables

from ddm.models.auth import ProjectTokenAuthenticator
from ddm.models.core import (
    DataDonation, DonationProject, QuestionnaireResponse, ResearchProfile,
    Participant, DonationBlueprint
)
from ddm.models.encryption import Decryption
from ddm.models.logs import EventLogEntry, ExceptionLogEntry
from ddm.models.serializers import (
    DonationSerializer, ResponseSerializer, ProjectSerializer, ParticipantSerializer
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, exceptions, permissions, status


def user_is_allowed(user, project):
    """
    Returns true if user is owner or collaborator of a project. False otherwise.
    """
    if user.is_anonymous:
        return False

    user_profile = ResearchProfile.objects.filter(user=user).first()
    if not user_profile:
        return False
    else:
        if project.owner != user_profile:
            return False
        else:
            return True


class DDMAPIMixin:
    """
    Mixin containing ddm-specific methods to be combined with DRF-views.
    """
    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        Added EventLog entries.
        """
        if request.authenticators and not request.successful_authenticator:
            self.create_event_log(
                descr='Failed Attempt',
                msg='Authentication failed.'
            )
            raise exceptions.NotAuthenticated()

        self.create_event_log(
            descr='Failed Attempt',
            msg='Permission Denied.'
        )
        raise exceptions.PermissionDenied(detail=message, code=code)

    def get_project(self):
        """ Returns project instance. """
        return DonationProject.objects.filter(pk=self.kwargs['pk']).first()

    def create_event_log(self, descr, msg):
        """ Creates an event log entry related to the current project. """
        if self.request is not None:
            prefix = f'{self.request.get_full_path()} {self.request.method}: '
        else:
            prefix = ''
        return EventLogEntry.objects.create(project=self.get_project(),
                                            description=f'{prefix}{descr}',
                                            message=msg)


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
        if not user_is_allowed(request.user, project):
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
        if not user_is_allowed(request.user, project):
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
        if not user_is_allowed(request.user, project):
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


class ExceptionAPI(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None, *args, **kwargs):
        """
        Log exception messages received from client.
        """
        project_id = self.kwargs['pk']
        project = DonationProject.objects.get(pk=project_id)

        try:
            participant_id = request.session[f'project-{project_id}']['participant_id']
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


class DonationsAPI(APIView, DDMAPIMixin):
    """
    Retrieve a set of Donations collected for a given Donation Project.

    This can be useful to create feedback dashboards for participants. For example,
    after completing a study, you could redirect your participants to another
    website where you retrieve the data donated by the participant and display
    some personalized insights. This can be useful to incentivize participation.

    Returns:
    - A Response object with data and status code.

    Available query filters:
    - participants: A comma separated list of external participant IDs
        belonging to the project whose donations should be returned
        (e.g. ?participants='ID1,ID2,ID3').
        If not specified, donations for all participants are returned.
    - blueprints: A comma separated list of file blueprint IDs, for which the
        donations should be returned (e.g. ?blueprints='BP-ID1,BP-ID2,BP-ID3').
        If not specified, donations for all blueprints associated with the
        project are returned.

    Example Usage:
    ```
    GET /api/project/<project_pk>/donations
    {
        "BP-Name": [[<donations participant A>], [<donations participant B>], ...],
        "BP2-Name": ...
    }
    ```

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 401 Unauthorized: If authentication fails.
    - 405 Method Not Allowed: If resources belonging to a super secret project
        are requested.

    Note:
    No identifying information is included in the returned object - i.e., no
    participant IDs are included. This means that if donations for multiple
    participants are requested, donations cannot be linked to specific
    participants.
    Please also note that this endpoint cannot be used for secret projects.
    """
    authentication_classes = [ProjectTokenAuthenticator]
    permission_classes = [permissions.IsAuthenticated]

    def get_blueprints(self, project):
        blueprints = self.request.query_params.get('blueprints')
        if blueprints is not None:
            return DonationBlueprint.objects.filter(
                project=project,
                pk__in=blueprints.split(',')
            )
        else:
            return DonationBlueprint.objects.filter(project=project)

    def get_donations(self, blueprint):
        participants = self.request.query_params.get('participants')
        if participants is not None:
            return blueprint.datadonation_set.filter(
                participant__external_id__in=participants.split(','))
        else:
            return blueprint.datadonation_set.all()

    @sensitive_variables()
    def get(self, request, format=None, *args, **kwargs):
        project = self.get_project()

        if project.super_secret:
            msg = 'Endpoint disabled for super secret projects.'
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                            data={'message': msg})

        blueprints = self.get_blueprints(project)
        try:
            decryptor = Decryption(project.secret_key, project.get_salt())
            donations = {}
            for blueprint in blueprints:
                blueprint_donations = self.get_donations(blueprint)
                donations[blueprint.name] = [DonationSerializer(d, decryptor=decryptor).data['data']
                                             for d in blueprint_donations]

        except ValueError:
            self.create_event_log(
                descr='Failed Attempt',
                msg='Download requested with incorrect secret.'
            )
            msg = 'Incorrect key material.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        response = Response(donations)
        self.create_event_log(
            descr='Data Download Successful',
            msg='The project data was downloaded.'
        )
        return response


class ResponsesAPI(APIView, DDMAPIMixin):
    """
    Retrieve a set of Questionnaire Responses collected for a given Donation Project.

    This can be useful to create feedback dashboards for participants. For example,
    after completing a study, you could redirect your participants to another
    website where you retrieve the data provided by the participant and display
    some personalized insights. This can be useful to incentivize participation.

    Returns:
    - A Response object with data and status code.

    Available query filters:
    - participants: A comma separated list of external participant IDs
        belonging to the project whose donations should be returned
        (e.g. ?participants='ID1,ID2,ID3').
        If not specified, donations for all participants are returned.

    Example Usage:
    ```
    GET /api/project/<project_pk>/responses
    [{'var_name_q1': 'answer', 'varname_q2': 'answer', ... },
     {<responses participant B>}, ...]
    ```

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 401 Unauthorized: If authentication fails.
    - 405 Method Not Allowed: If resources belonging to a super secret project
        are requested.

    Note:
    No identifying information is included in the returned object - i.e., no
    participant IDs are included. This means that if responses for multiple
    participants are requested, responses cannot be linked to specific
    participants.
    Please also note that this endpoint cannot be used for secret projects.
    """
    authentication_classes = [ProjectTokenAuthenticator]
    permission_classes = [permissions.IsAuthenticated]

    def get_responses(self, project):
        participants = self.request.query_params.get('participants')
        if participants is not None:
            return QuestionnaireResponse.objects.filter(
                project=project, participant__external_id__in=participants.split(','))
        else:
            return QuestionnaireResponse.objects.filter(project=project)

    @sensitive_variables()
    def get(self, request, format=None, *args, **kwargs):
        project = self.get_project()

        if project.super_secret:
            msg = 'Endpoint disabled for super secret projects.'
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                            data={'message': msg})

        try:
            decryptor = Decryption(project.secret_key, project.get_salt())
            responses = [ResponseSerializer(r, decryptor=decryptor).data['responses']
                         for r in self.get_responses(project)]

        except ValueError:
            self.create_event_log(
                descr='Failed Attempt',
                msg='Download requested with incorrect secret.'
            )
            msg = 'Incorrect key material.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        response = Response(responses)
        self.create_event_log(
            descr='Data Download Successful',
            msg='The project data was downloaded.'
        )
        return response
