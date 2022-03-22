from django.shortcuts import redirect
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
    current_step = None
    participant = None
    project_session = None
    state = None

    def get(self, request, *args, **kwargs):
        self.initialize_values(request)

        target = self.get_target()
        if target == self.view_name:
            context = self.get_context_data(object=self.object)
            self.project_session['steps'][self.view_name]['state'] = 'started'
            return self.render_to_response(context)
        else:
            return redirect(target, slug=self.object.slug)

    def initialize_values(self, request):
        self.object = self.get_object()
        self.current_step = self.steps.index(self.view_name)

        # Set Session
        if not request.session.get('projects'):
            request.session['projects'] = {}
            self.register_project(request)
        elif not request.session['projects'].get(f'{self.object.pk}'):
            self.register_project(request)
        self.project_session = request.session['projects'][f'{self.object.pk}']

        # Set state
        self.state = self.project_session['steps'][self.view_name]['state']

        # Set Participant
        self.register_participant()
        return

    def register_project(self, request):
        request.session['projects'][f'{self.object.pk}'] = {
            'steps': {},
            'data': {},
            'completed': False,
            'participant_id': None
        }
        for step in self.steps:
            request.session['projects'][f'{self.object.pk}']['steps'][step] = {
                'state': 'not started'
            }
        return

    def register_participant(self):
        participant_id = self.project_session['participant_id']
        try:
            self.participant = Participant.objects.get(pk=participant_id)
        except Participant.DoesNotExist:
            self.participant = Participant.objects.create(
                project=self.object,
                start_time=timezone.now()
            )
            self.project_session['participant_id'] = self.participant.id
        return

    def get_target(self):
        if self.state == 'started':
            target = self.view_name
        elif self.state == 'not started':  # Search backward.
            target = self.search_target_backward(self.view_name)
        elif self.state == 'completed':  # Search forward.
            target = self.search_target_forward(self.view_name)
            pass
        return target

    def search_target_backward(self, view_name):
        curr_step_index = self.steps.index(view_name)
        if curr_step_index == 0:
            target = view_name
        else:
            next_step = self.steps[curr_step_index - 1]
            next_step_state = self.project_session['steps'][next_step]['state']
            if next_step_state == 'completed':
                target = view_name
            elif next_step_state == 'started':
                target = next_step
            else:
                target = self.search_target_backward(next_step)
        return target

    def search_target_forward(self, view_name):
        curr_step_index = self.steps.index(view_name)
        if curr_step_index == len(self.steps) - 1:
            target = view_name
        else:
            next_step = self.steps[curr_step_index + 1]
            next_step_state = self.project_session['steps'][next_step]['state']
            if next_step_state != 'completed':
                target = next_step
            else:
                target = self.search_target_forward(next_step)
        return target

    def set_step_complete(self):
        self.project_session['steps'][self.view_name]['state'] = 'completed'
        return

    def post(self, request, *arges, **kwargs):
        self.initialize_values(request)
        self.set_step_complete()
        return redirect(self.steps[self.current_step + 1],
                        slug=self.object.slug)


class ProjectEntry(ProjectBaseView):
    template_name = 'ddm/public/entry_page.html'
    view_name = 'project-entry'

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        return redirect(self.steps[self.current_step + 1],
                        slug=self.object.slug)


class ProjectExit(ProjectBaseView):
    template_name = 'ddm/public/end.html'
    view_name = 'project-exit'

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
