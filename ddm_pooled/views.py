from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated

from ddm.models.core import DonationProject
from ddm_pooled.models import PoolParticipant, PooledProject
from ddm_pooled.serializers import ParticipantSerializer
from ddm_pooled.settings import POOL_KW, PROJECT_KW
from ddm_pooled.utils import get_participant_from_request


class PoolDonateView(DetailView):
    model = DonationProject
    template_name = 'ddm_pooled/pool_donation_consent.html'
    success_url = 'DebriefingView'
    context_object_name = 'project'

    def post(self, request, *args, **kwargs):
        """
        Checks whether participant has provided donation consent to continue with
        the study.
        """
        pooled_project = self.get_pool_project()
        if pooled_project.get_donation_consent:
            return self.check_consent(request, **kwargs)

        return super().post(request, **kwargs)

    def check_consent(self, request, **kwargs):
        """
        Checks whether post data contains information on donation consent.
        Re-Renders view with error message if donation information is invalid.
        Renders debriefing view otherwise.
        """
        # Check that answer has been provided and is valid.
        consent = request.POST.get('donation_consent', None)
        if consent not in ['0', '1']:
            # Render briefing view again with error message.
            self.object = self.get_object()
            context = self.get_context_data(object=self.get_object())
            context.update({'consent_error': True})
            return self.render_to_response(context)

        participant = get_participant_from_request(request, self.get_object())
        pool_participant = PoolParticipant.objects.get(participant=participant)
        if consent == '1':
            pool_participant.pool_donate = True
        elif consent == '0':
            pool_participant.pool_donate = False

        pool_participant.save()
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool_project'] = self.get_pool_project()
        return context

    def get_pool_project(self):
        try:
            return PooledProject.objects.get(project=self.get_object())
        except PooledProject.DoesNotExist:
            raise Http404()

    def get_success_url(self):
        return reverse('debriefing', kwargs={'slug': self.get_object().slug})


class ParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """ ViewSet for getting general participation information for a specific subset of a PooledProject """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        project_id = self.request.query_params.get(PROJECT_KW, None)
        pool_id = self.request.query_params.get(POOL_KW, None)
        if pool_id is not None:
            return PoolParticipant.objects.filter(
                pool_id=pool_id, pooled_project__external_id=project_id)
        else:
            raise ParseError()


# TODO: Implement class DonationAPI(APIView):
