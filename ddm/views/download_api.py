from django.views.decorators.debug import sensitive_variables

from ddm.models.auth import ProjectTokenAuthenticator
from ddm.models.core import (
    DataDonation, DonationProject, QuestionnaireResponse, ResearchProfile,
    Participant
)
from ddm.models.logs import EventLog
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
            EventLog.objects.create(
                project=self.get_project(),
                description=f'Failed {request.method} Attempt',
                message='Authentication failed.'
            )
            raise exceptions.NotAuthenticated()

        EventLog.objects.create(
            project=self.get_project(),
            description=f'Failed {request.method} Attempt',
            message='Permission Denied.'
        )
        raise exceptions.PermissionDenied(detail=message, code=code)

    def get_project(self):
        """ Returns project instance. """
        return DonationProject.objects.filter(pk=self.kwargs['pk']).first()

    @sensitive_variables()
    def get(self, request, format=None, *args, **kwargs):
        """
        Return a dictionary object containing the data donations and
        questionnaire responses.
        """
        project = self.get_project()
        if not user_is_allowed_to_download(request.user, project):
            EventLog.objects.create(
                project=project,
                description='Forbidden Download Request',
                message='Request user is not permitted to download the data.'
            )
            msg = 'User does not have access.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        if not project.super_secret:
            secret = None
        else:
            secret = None if 'Super-Secret' not in request.headers else request.headers['Super-Secret']
            if not secret:
                EventLog.objects.create(
                    project=project,
                    description='Failed Download Attempt',
                    message='Download requested without supplying secret.'
                )
                msg = 'Incorrect key material.'
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'message': msg})

        data_donations = DataDonation.objects.filter(project=project)
        q_responses = QuestionnaireResponse.objects.filter(project=project)

        try:
            results = {
                'project': ProjectSerializer(project).data,
                'donations': [DonationSerializer(d, secret=secret).data for d in data_donations],
                'responses': [ResponseSerializer(r, secret=secret).data for r in q_responses],
            }
        except ValueError:
            EventLog.objects.create(
                project=project,
                description='Failed Download Attempt',
                message='Download requested with incorrect secret.'
            )
            msg = 'Incorrect key material.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        EventLog.objects.create(
            project=project,
            description='Data Download Successful',
            message='The project data was downloaded.'
        )

        return Response(status=status.HTTP_200_OK, data=results)

    def delete(self, request, format=None, *args, **kwargs):
        """
        Delete data donations and questionnaire requests associated with project.
        """
        project = self.get_project()
        if not user_is_allowed_to_download(request.user, project):
            EventLog.objects.create(
                project=project,
                description='Forbidden Deletion Request',
                message='Request user is not permitted to delete '
                        'the project data.'
            )
            msg = 'User does not have access.'
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'message': msg})

        # Delete all related objects.
        Participant.objects.filter(project=project).delete()
        n_deleted_donations = DataDonation.objects.filter(project=project).delete()[0]
        n_deleted_responses = QuestionnaireResponse.objects.filter(project=project).delete()[0]

        EventLog.objects.create(
            project=project,
            description='Data Deletion Successful',
            message='The project data was deleted.'
        )

        msg = (f'Deleted {n_deleted_donations} data donations and '
               f'{n_deleted_responses} questionnaire responses.')
        return Response(status=status.HTTP_200_OK, data={'message': msg})
