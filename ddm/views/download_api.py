from django.http import Http404, HttpResponseBadRequest
from django.views.decorators.debug import sensitive_variables

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


class ProjectDataView(APIView):
    """
    Download or delete data collected within a project.

    * Token authentication for remote calls.
    * Session authentication for browser access.
    * Only project owners are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @sensitive_variables('secret')
    def get(self, request, format=None, *args, **kwargs):
        """
        Return a dictionary object containing the data donations and
        questionnaire responses.
        """
        project_id = self.kwargs['pk']
        project = DonationProject.objects.get(pk=project_id)
        if not user_is_allowed_to_download(request.user, project):
            raise Http404()

        if project.super_secret:
            secret = None if 'super_secret' not in request.headers else request.headers['super_secret']

            if not secret:
                # TODO: Add this to admin log.
                return HttpResponseBadRequest('super_secret required but not found in headers.')

            project.secret_key = secret

        data_donations = DataDonation.objects.filter(project=project)
        q_responses = QuestionnaireResponse.objects.filter(project=project)

        results = {
            'project': ProjectSerializer(project).data,
            'donations': [DonationSerializer(d).data for d in data_donations],
            'responses': [ResponseSerializer(r).data for r in q_responses],
        }
        return Response(results)

    def delete(self, request, format=None, *args, **kwargs):
        """
        Delete data donations and questionnaire requests associated with project.
        """
        project_id = self.kwargs['pk']
        project = DonationProject.objects.get(pk=project_id)
        if not user_is_allowed_to_download(request.user, project):
            raise Http404()

        # Delete all related objects.
        Participant.objects.filter(project=project).delete()
        n_deleted_donations = DataDonation.objects.filter(project=project).delete()[0]
        n_deleted_responses = QuestionnaireResponse.objects.filter(project=project).delete()[0]

        response_data = {
            'Deleted Donations': n_deleted_donations,
            'Deleted Responses': n_deleted_responses
        }
        return Response(status=status.HTTP_204_NO_CONTENT, data=response_data)
