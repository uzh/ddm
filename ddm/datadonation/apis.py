from django.views.decorators.debug import sensitive_variables
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from ddm.auth.models import ProjectTokenAuthenticator
from ddm.core.apis import DDMAPIMixin
from ddm.datadonation.models import DonationBlueprint
from ddm.datadonation.serializers import DonationSerializer
from ddm.encryption.models import Decryption


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
