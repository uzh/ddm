from django.core.exceptions import BadRequest, ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.debug import sensitive_variables
from rest_framework import exceptions, permissions, authentication, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from ddm.apis.serializers import (
    DataDonationSerializer, ResponseSerializer, ParticipantSerializer,
    ResponseSerializerWithSnapshot, ProjectSerializer
)
from ddm.auth.models import ProjectTokenAuthenticator
from ddm.auth.utils import user_has_project_access
from ddm.encryption.models import Decryption
from ddm.logging.models import EventLogEntry
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.questionnaire.models import QuestionnaireResponse


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
                descr='Failed Attempt', msg='Authentication failed.')
            raise exceptions.NotAuthenticated()

        self.create_event_log(
            descr='Failed Attempt', msg='Permission Denied.')
        raise exceptions.PermissionDenied(detail=message, code=code)

    def get_project(self):
        """ Returns project instance. """
        project_id = self.kwargs.get('project_url_id')
        return get_object_or_404(DonationProject, url_id=project_id)

    def create_event_log(self, descr, msg):
        """ Creates an event log entry related to the current project. """
        if self.request is not None:
            prefix = f'{self.request.get_full_path()} {self.request.method}: '
        else:
            prefix = ''
        return EventLogEntry.objects.create(
            project=self.get_project(), description=f'{prefix}{descr}', message=msg)


class ProjectDetailApiView(ListAPIView, DDMAPIMixin):
    """
    API View to retrieve detail information about a specific project.

    This view handles requests to fetch project-related metadata,
    including information participants, blueprint configuration, and project
    configuration.

    Returns:
    - A Response object with data and status code.

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 401 Unauthorized: If authentication fails.
    """
    project = None
    authentication_classes = [ProjectTokenAuthenticator]
    permission_classes = [permissions.IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project = self.get_project()
        except Http404 as e:
            raise Http404(str(e))
        return super().dispatch(request, *args, **kwargs)

    def get_participants(self):
        return self.project.participant_set.all()

    def get_blueprints(self):
        return self.project.donationblueprint_set.all()

    def get_blueprints_info(self, blueprints):
        blueprints_info = []
        for blueprint in blueprints:
            blueprints_info.append(blueprint.get_config())
        return blueprints_info

    def get(self, request, format=None, *args, **kwargs):
        participants = self.get_participants()

        blueprints = self.get_blueprints()
        blueprints_info = self.get_blueprints_info(blueprints)

        response = {
            'participants': ParticipantSerializer(participants, many=True).data,
            'blueprints': blueprints_info,
            'project': ProjectSerializer(self.project).data,
            'metadata': {
                'n_blueprints': len(blueprints),
                'n_participants': len(participants)
            }
        }
        self.create_event_log(
            descr='API access: Project details retrieved.',
            msg='The project detail data were accessed through the API.'
        )
        return Response(response)


class ProjectDonationsListView(ListAPIView, DDMAPIMixin):
    """
    API View to retrieve the donations collected in a project.

    Returns:
    - A Response object with data and status code.

    Available query filters:
    - participants (required): A comma separated list of external participant IDs
        belonging to the project whose donations should be returned
        (e.g. ?participants='ID1,ID2,ID3').
        If not specified, no data is returned.
    - blueprints (optional): A comma separated list of file blueprint IDs, for which the
        donations should be returned (e.g. ?blueprints='BP-ID1,BP-ID2,BP-ID3').
        If not specified, donations for all blueprints associated with the
        project are returned.

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 401 Unauthorized: If authentication fails.
    - 405 Method Not Allowed: If resources belonging to a super secret project
        are requested.

    Note:
    Please note that this endpoint cannot be used for secret projects.
    """
    authentication_classes = [ProjectTokenAuthenticator]
    permission_classes = [permissions.IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project = self.get_project()
        except Http404 as e:
            raise Http404(str(e))
        return super().dispatch(request, *args, **kwargs)

    def get_participants(self, project):
        participants = project.participant_set.all()
        participant_param = self.request.query_params.get('participants')
        if participant_param is None:
            raise BadRequest('Required parameter "participants" is missing.')
        participant_ids = participant_param.split(',')
        return participants.filter(external_id__in=participant_ids)

    def get_blueprints(self, project):
        blueprints = project.donationblueprint_set.all()
        blueprint_param = self.request.query_params.get('blueprints')
        if blueprint_param is None:
            return blueprints
        else:
            blueprint_ids = blueprint_param.split(',')
            return blueprints.filter(pk__in=blueprint_ids)

    def get_donations(self, blueprint, participants):
        donations = blueprint.datadonation_set.filter(
            participant__in=participants)
        return donations

    def get_metadata(self, project):
        return

    @sensitive_variables()
    def get(self, request, format=None, *args, **kwargs):
        if self.project.super_secret:
            raise exceptions.MethodNotAllowed(
                'GET', detail='Endpoint disabled for super secret projects.')

        participants = self.get_participants(self.project)
        blueprints = self.get_blueprints(self.project)

        response = {
            'blueprints': {},
            'metadata': {
                'n_blueprints': len(blueprints)
            }
        }

        decryptor = Decryption(self.project.secret_key, self.project.get_salt())
        for blueprint in blueprints:
            donations = self.get_donations(blueprint, participants)
            response['blueprints'][f'{blueprint.pk}'] = {
                'blueprint_name': blueprint.name,
                'donations': DataDonationSerializer(donations, many=True, decryptor=decryptor).data
            }

        self.create_event_log(
            descr='API access: Donations retrieved.',
            msg='The donation data was accessed through the API.'
        )
        return Response(response)


class ResponsesApiView(ListAPIView, DDMAPIMixin):
    """
    API View to retrieve the questionnaire responses for a project.

    Returns:
    - A Response object with data and status code.

    Available query filters:
    - participants (optional): A comma-separated list of external participant IDs
        belonging to the project whose donations should be returned
        (e.g. "?participants=ID1,ID2,ID3").
    - include_snapshot (optional): If include_snapshot is 'true', the response
        includes a snapshot of the questionnaire configuration at
        the time the questionnaire was completed for each participant.
        Otherwise, it is omitted.

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 401 Unauthorized: If authentication fails.
    """
    project = None
    authentication_classes = [ProjectTokenAuthenticator]
    permission_classes = [permissions.IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project = self.get_project()
        except Http404 as e:
            raise Http404(str(e))
        return super().dispatch(request, *args, **kwargs)

    def get_participants(self):
        participants = self.project.participant_set.all()
        participant_param = self.request.query_params.get('participants')
        if participant_param is None:
            return participants
        else:
            participant_ids = participant_param.split(',')
            return participants.filter(external_id__in=participant_ids)

    def get_responses(self, participants):
        return QuestionnaireResponse.objects.filter(
                project=self.project, participant__in=participants)

    def get_serializer(self):
        snapshot_parameter = self.request.query_params.get('include_snapshot')
        if snapshot_parameter == 'true':
            return ResponseSerializerWithSnapshot
        else:
            return ResponseSerializer

    def get_metadata(self, responses):
        metadata = {
            'n_responses': len(responses)
        }
        return metadata

    def get(self, request, format=None, *args, **kwargs):
        participants = self.get_participants()
        responses = self.get_responses(participants)
        decryptor = Decryption(self.project.secret_key, self.project.get_salt())
        serializer = self.get_serializer()

        response = {
            'responses': serializer(responses, many=True, decryptor=decryptor).data,
            'metadata': self.get_metadata(responses)
        }
        self.create_event_log(
            descr='API access: Responses retrieved',
            msg='The response data was accessed through the API.'
        )
        return Response(response)


class DeleteParticipantAPI(APIView, DDMAPIMixin):
    """
    Delete a participant by providing their external ID.

    Returns:
    - A Response object with the status code.

    Authentication Methods:
    - Token authentication for remote calls.
    - Session authentication for access through web application (by verifying
        that the requesting user is the project owner).

    Error Responses:
    - 401 Unauthorized: If authentication fails.
    - 403 Forbidden: If a user is not permitted to access a project.
    - 404 Not Found: No participant could be found for the provided ID.
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
            descr=f'Participant with external id "{external_id}" was deleted.',
            msg='Participant deleted.'
        )

        msg = f'Participant with external id "{external_id}" successfully deleted.'
        return Response(status=status.HTTP_200_OK, data={'message': msg})
