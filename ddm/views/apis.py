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
from ddm.models.logs import EventLogEntry, ExceptionLogEntry
from ddm.models.serializers import (
    DonationSerializer, ResponseSerializer, ProjectSerializer
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, exceptions, permissions, status


def user_is_allowed_to_download(user, project):
    """
    Returns true if user is owner or collaborator of a project. False otherwise.
    """
    user_profile = ResearchProfile.objects.filter(user=user).first()
    if not user_profile:
        return False
    else:
        if project.owner != user_profile:
            return False
        else:
            return True


class ProjectDataAPI(APIView):
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
                descr=f'Failed {request.method} Attempt',
                msg='Authentication failed.'
            )
            raise exceptions.NotAuthenticated()

        self.create_event_log(
            descr=f'Failed {request.method} Attempt',
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

    @sensitive_variables()
    def get(self, request, format=None, *args, **kwargs):
        """
        Return a zip container that contains a json file which holds the
        data donations and questionnaire responses.
        """
        project = self.get_project()
        if not user_is_allowed_to_download(request.user, project):
            self.create_event_log(
                descr='Forbidden Download Request',
                msg='Request user is not permitted to download the data.'
            )
            msg = 'User does not have access.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        # Extract secret from request if project is super secret.
        kwargs = {}
        if project.super_secret:
            secret = None if 'Super-Secret' not in request.headers else request.headers['Super-Secret']
            if secret is None:
                self.create_event_log(
                    descr='Failed Download Attempt',
                    msg='Download requested without supplying secret.'
                )
                msg = 'Incorrect key material.'
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'message': msg})
            else:
                kwargs['secret'] = secret

        # Gather project data in dictionary.
        data_donations = DataDonation.objects.filter(project=project)
        q_responses = QuestionnaireResponse.objects.filter(project=project)
        try:
            results = {
                'project': ProjectSerializer(project).data,
                'donations': [DonationSerializer(d, **kwargs).data for d in data_donations],
                'responses': [ResponseSerializer(r, **kwargs).data for r in q_responses],
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

    def delete(self, request, format=None, *args, **kwargs):
        """
        Delete data donations and questionnaire requests associated with project.
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


class ParticipantAPI(APIView):
    """
    Delete a participant of an owned project by providing their external ID.

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


class ExceptionAPI(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None, *args, **kwargs):
        """
        Log exception messages received from client.
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
