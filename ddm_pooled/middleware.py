from ddm.models.core import DonationProject, Participant
from ddm.views.participation_flow import (
    BriefingView, DebriefingView, DataDonationView, create_participation_session
)
from ddm_pooled.models import PooledProject, PoolParticipant
from ddm_pooled.settings import POOL_KW
from ddm_pooled.utils import get_participant_from_request
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class PooledProjectMiddleware(MiddlewareMixin):
    """
    Middleware to manage, create, and update pooled models (PooledProject and
    PoolParticipant) during study participation (i.e., middleware only applies
    to views defined in ddm.views.participation_flow).

    Reroutes to pool donation question before debriefing view (if enabled for
    a given PoolProject).
    """

    def _init_(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        project = self.get_project(view_kwargs)
        pooled_project = self.get_pooled_project_or_none(project)
        if not pooled_project:
            return

        if hasattr(view_func, 'view_class'):
            view_class = view_func.view_class

            if view_class is BriefingView:
                create_participation_session(request, project)
                required_params = [POOL_KW]
                if not all(p in request.GET for p in required_params):
                    # TODO: add general information or render exception view
                    pass

                try:
                    participant = get_participant_from_request(request, project)
                except (KeyError, Participant.DoesNotExist):
                    return

                try:
                    PoolParticipant.objects.get(participant=participant)
                except PoolParticipant.DoesNotExist:
                    PoolParticipant.objects.create(
                        participant=participant,
                        pool_id=request.GET.get(POOL_KW, 'default_pool'),
                        pooled_project=pooled_project
                    )

                return

            if view_class is DataDonationView:
                request.project_is_pooled = True
                return

            if view_class is DebriefingView:
                try:
                    participant = PoolParticipant.objects.get(
                        participant=get_participant_from_request(request, project))
                except (KeyError, Participant.DoesNotExist,
                        PoolParticipant.DoesNotExist):
                    return

                if pooled_project.get_donation_consent and participant.pool_donate is None:
                    return redirect(reverse('ddm-pool-donate', args=[project.slug]))
                else:
                    return

        return

    @staticmethod
    def get_project(view_kwargs):
        project_slug = view_kwargs.get('slug', None)
        project = DonationProject.objects.filter(slug=project_slug).first()
        return project

    @staticmethod
    def get_pooled_project_or_none(project):
        try:
            return PooledProject.objects.get(project=project)
        except PooledProject.DoesNotExist:
            return None
