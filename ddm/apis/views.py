import csv
import io

from django.core.exceptions import BadRequest, ObjectDoesNotExist
from django.http import Http404, StreamingHttpResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
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
from ddm.datadonation.models import DataDonation
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
    - A Response object with the data as JSON or CSV and status code.

    Available query filters:
    - participants (optional): A comma-separated list of external participant IDs
        belonging to the project whose donations should be returned
        (e.g. "?participants=ID1,ID2,ID3").
    - include_snapshot (optional): If include_snapshot is 'true', the response
        includes a snapshot of the questionnaire configuration at
        the time the questionnaire was completed for each participant.
        Otherwise, it is omitted.
    - csv (optional): If csv is 'true', the response will be provided
        as a csv file.

    Error Responses:
    - 400 Bad Request: If there's an issue with the input data.
    - 403 Unauthorized: If authentication fails.
    """
    project = None
    authentication_classes = [
        authentication.SessionAuthentication,
        ProjectTokenAuthenticator
    ]
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
        snapshot = self.request.query_params.get('include_snapshot')
        if snapshot == 'true':
            return ResponseSerializerWithSnapshot
        else:
            return ResponseSerializer

    def get_metadata(self, responses):
        metadata = {
            'n_responses': len(responses)
        }
        return metadata

    def create_json_response(self, responses, decryptor):
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

    def create_csv_response(self, responses, decryptor):
        clean_responses = []
        col_names = {'participant', 'time_submitted'}
        responses = ResponseSerializer(responses, many=True, decryptor=decryptor).data
        for response in responses:
            data = dict()
            data['participant'] = response['participant']
            data['time_submitted'] = response['time_submitted']
            for var, val in response['response_data'].items():
                col_names.add(var)
                data[var] = val
            clean_responses.append(data)

        csv_output = io.StringIO()
        writer = csv.DictWriter(csv_output, fieldnames=col_names)
        writer.writeheader()
        writer.writerows(clean_responses)

        csv_content = csv_output.getvalue()
        csv_output.close()

        filename = f'ddm_responses_{self.project.url_id}'
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        return response

    def get(self, request, format=None, *args, **kwargs):
        participants = self.get_participants()
        responses = self.get_responses(participants)
        decryptor = Decryption(self.project.secret_key, self.project.get_salt())

        if self.request.query_params.get('csv') == 'true':
            return self.create_csv_response(responses, decryptor)
        else:
            return self.create_json_response(responses, decryptor)


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

    Note: Description currently not included in the researcher documentation
    because this view can only be called from within the application.
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


class DownloadProjectDetailsView(APIView, DDMAPIMixin):
    """
    Returns a CSV file containing high level participation information for a
    project.

    Each line of the CSV file represents one participant and holds the following
    information:
    - participant ID
    - start time of participation
    - end time of participation
    - current step of participation
    - completed (boolean)
    - extra data collected on participant-level
    - download link for donations
    - for each blueprint:
    -- name
    -- time submitted
    -- consent
    -- status

    Returns a StreamingHttpResponse.
    """
    authentication_classes = [authentication.SessionAuthentication]
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

    def get_donations(self, participant):
        return participant.datadonation_set.all()

    def get_csv_header(self, blueprints):
        participant_header = self.get_participant_header()
        blueprint_header = self.get_blueprint_header(blueprints)
        return participant_header + blueprint_header + 'donation_download_link\n'

    @staticmethod
    def get_participant_header():
        participant_header = (
            'participant_id,'
            'start_time,'
            'end_time,'
            'current_step,'
            'completed,'
            'extra_data,'
        )
        return participant_header

    @staticmethod
    def get_participant_data(participant):
        participant_info = (
            f'"{participant.external_id}",'
            f'"{participant.start_time}",'
            f'"{participant.end_time}",'
            f'"{participant.current_step}",'
            f'"{participant.completed}",'
            f'"{participant.extra_data}",'
        )
        return participant_info

    @staticmethod
    def get_blueprint_header(blueprints):
        header = ''
        for blueprint in blueprints:
            pk = blueprint.pk
            blueprint_header = (
                f'blueprint_{pk}_name,'
                f'blueprint_{pk}_time_submitted,'
                f'blueprint_{pk}_consent,'
                f'blueprint_{pk}_status,'
            )
            header += blueprint_header
        return header

    def get_blueprint_donation_data(self, blueprints, participant):
        blueprint_data = ''
        n_donations = 0
        donations = self.get_donations(participant)
        for blueprint in blueprints:
            donation = donations.filter(blueprint=blueprint).first()
            if donation:
                data = (
                    f'"{blueprint.name}",'
                    f'"{donation.time_submitted}",'
                    f'"{donation.consent}",'
                    f'"{donation.status}",'
                )
                n_donations += 1
            else:
                data = (
                    f'{None},'
                    f'{None},'
                    f'{None},'
                    f'{None},'
                )
            blueprint_data += data

        if n_donations > 0:
            blueprint_data += self.get_download_link(participant)
        else:
            blueprint_data += f'{None}'
        return blueprint_data

    def get_download_link(self, participant):
        url = reverse(
            'ddm_datadonation:download_donation',
            args=[self.project.url_id, participant.external_id]
        )
        return self.request.build_absolute_uri(url)

    def generate_csv(self):
        blueprints = self.get_blueprints()
        header = self.get_csv_header(blueprints)
        yield header

        # Loop through participants
        participants = self.get_participants()
        n_rows = 0
        data = ''
        for participant in participants:
            participant_data = self.get_participant_data(participant)
            blueprint_data = self.get_blueprint_donation_data(blueprints, participant)
            data += (participant_data + blueprint_data + '\n')
            n_rows += 1
            if n_rows % 10 == 0:
                yield data
                data = ''
        yield data

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to stream JSON response.
        """
        if not user_has_project_access(request.user, self.project):
            self.create_event_log(
                descr='Forbidden Deletion Request',
                msg='Request user is not permitted to delete the project data.'
            )
            msg = 'User does not have access.'
            raise exceptions.PermissionDenied(msg)

        response = StreamingHttpResponse(
            self.generate_csv(),
            content_type='text/json'
        )
        filename = f'project_{self.project.url_id}_details.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
