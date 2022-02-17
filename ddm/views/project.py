from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic.detail import DetailView

from ddm.models import DonationProject, Participant


class ProjectBaseView(DetailView):
    model = DonationProject
    context_object_name = 'project'
    steps = [
        'project-entry',
        'data-donation',
        'questionnaire',
        'project-exit'
    ]
    view_name = None
    project_session = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        request = self.register_project_in_session(request)
        request = self.register_participant_in_session(request)

        # TODO: This approach is inefficient => Change this.
        target = self.get_target()

        context = self.get_context_data(object=self.object)
        context['part_id'] = self.project_session['participant_id']

        if target == self.view_name:
            print('pass')
            self.project_session['steps'][self.view_name]['state'] = 'started'
            print(self.project_session)
            print(request.session['projects'][f'{self.object.pk}'])
            print(target)
            context['session'] = request.session['projects']
            return self.render_to_response(context)
        else:
            return redirect(target)

    def set_step_complete(self):
        self.project_session['steps'][self.view_name]['state'] = 'completed'
        return

    def get_target(self):
        # Check if project has already been started.
        if self.project_session['steps'][self.view_name]['state'] == 'not started':
            # Check if it is the first step:
            if self.steps.index(self.view_name) == 0:
                target = self.view_name
            else:
                target = self.search_target(self.view_name)
        return target

    def search_target(self, view_name):
        prev_view = self.steps.index(view_name)
        if self.project_session['steps'][self.view_name]['state'] == 'completed':
            target = view_name
        elif self.project_session['steps'][self.view_name]['state'] == 'started':
            target = prev_view
        else:
            target = self.search_target(prev_view)
        return target

    def register_project_in_session(self, request):
        if not request.session.get('projects'):
            request.session['projects'] = {}

        if not request.session['projects'].get(f'{self.object.pk}'):
            request.session['projects'][f'{self.object.pk}'] = {
                'steps': {},
                'data': {},
                'completed': False,
                'participant_id': None
            }
        self.project_session = request.session['projects'][f'{self.object.pk}']
        for step in self.steps:
            self.project_session['steps'][step] = {'state': 'not started'}
        return request

    def register_participant_in_session(self, request):
        participant_id = self.project_session['participant_id']
        try:
            Participant.objects.get(pk=participant_id)
        except Participant.DoesNotExist:
            participant = Participant.objects.create(
                project=self.object,
                start_time=timezone.now()
            )
            self.project_session['participant_id'] = participant.id
        return request

    def update_request_session(self, request):
        request.session['projects'][f'{self.object.pk}'] = self.project_session
        return request


class ProjectEntry(ProjectBaseView):
    template_name = 'ddm/project/entry_page.html'
    view_name = 'project-entry'

    def post(self, request, *args, **kwargs):
        self.set_step_complete()
        current_step = self.steps.index(self.view_name)
        return redirect(self.steps[current_step + 1])
