from django.views.generic.detail import DetailView
from django.utils import timezone

from ddm.models import DonationProject, Participant


class ProjectEntry(DetailView):
    model = DonationProject
    context_object_name = 'project'
    template_name = 'ddm/project/entry_page.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        request = self.register_project_in_session(request)
        request = self.register_participant_in_session(request)
        # TODO: Check if participant is on correct page or if should be
        #  redirected. => maybe define these functions in a project baseview

        context = self.get_context_data(object=self.object)
        context['part_id'] = request.session['projects'][f'{self.object.pk}']['part_id']
        return self.render_to_response(context)

    def register_project_in_session(self, request):
        # Register project in session.
        if not request.session.get('projects'):
            request.session['projects'] = {}

        if not request.session['projects'].get(f'{self.object.pk}'):
            request.session['projects'][f'{self.object.pk}'] = {
                'part_id': None
            }
        return request

    def register_participant_in_session(self, request):
        part_pk = request.session['projects'][f'{self.object.pk}']['part_id']
        try:
            Participant.objects.get(pk=part_pk)
        except Participant.DoesNotExist:
            part = Participant.objects.create(
                project=self.object,
                start_time=timezone.now()
            )
            request.session['projects'][f'{self.object.pk}']['part_id'] = part.pk
        return request
