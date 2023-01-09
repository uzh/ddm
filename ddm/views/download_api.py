from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.debug import sensitive_variables

from ddm.models.auth import ProjectTokenAuthenticator
from ddm.models.core import DataDonation, DonationProject, QuestionnaireResponse, ResearchProfile, Participant
from ddm.models.serializers import DonationSerializer, ResponseSerializer, ProjectSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status


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


# TODO: Log these actions somewhere.
class ProjectDataView(APIView):
    """
    Download or delete data collected within a project.

    * Token authentication for remote calls.
    * Session authentication for browser access.
    * Only project owners are able to access this view.
    """
    authentication_classes = [ProjectTokenAuthenticator, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @sensitive_variables()
    def get(self, request, format=None, *args, **kwargs):
        """
        Return a dictionary object containing the data donations and
        questionnaire responses.
        """
        project_id = self.kwargs['pk']
        project = DonationProject.objects.get(pk=project_id)
        if not user_is_allowed_to_download(request.user, project):
            return HttpResponseForbidden('User does not have access.')

        if not project.super_secret:
            secret = None
        else:
            secret = None if 'Super-Secret' not in request.headers else request.headers['Super-Secret']
            if not secret:
                # TODO: Add this to admin log
                return HttpResponseForbidden('Incorrect key material.')

        data_donations = DataDonation.objects.filter(project=project)
        q_responses = QuestionnaireResponse.objects.filter(project=project)

        try:
            results = {
                'project': ProjectSerializer(project).data,
                'donations': [DonationSerializer(d, secret=secret).data for d in data_donations],
                'responses': [ResponseSerializer(r, secret=secret).data for r in q_responses],
            }
        except ValueError:
            return HttpResponseForbidden('Incorrect key material.')

        return Response(results)

    def delete(self, request, format=None, *args, **kwargs):
        """
        Delete data donations and questionnaire requests associated with project.
        """
        project_id = self.kwargs['pk']
        project = DonationProject.objects.get(pk=project_id)
        if not user_is_allowed_to_download(request.user, project):
            return HttpResponseForbidden('User does not have access.')

        # Delete all related objects.
        Participant.objects.filter(project=project).delete()
        n_deleted_donations = DataDonation.objects.filter(project=project).delete()[0]
        n_deleted_responses = QuestionnaireResponse.objects.filter(project=project).delete()[0]

        response_data = {
            'Deleted Donations': n_deleted_donations,
            'Deleted Responses': n_deleted_responses
        }
        return Response(status=status.HTTP_204_NO_CONTENT, data=response_data)
