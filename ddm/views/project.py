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
    project_session = None

    def get(self, request, *args, **kwargs):
        self.set_values()
        request = self.register_project_in_session(request)
        request = self.register_participant_in_session(request)

        # TODO: This approach might be inefficient => Check this.
        target = self.get_target()

        context = self.get_context_data(object=self.object)
        context['part_id'] = self.project_session['participant_id']

        if target == self.view_name:
            self.project_session['steps'][self.view_name]['state'] = 'started'
            request.session['projects'][f'{self.object.pk}'] = self.project_session.copy()
            context['session'] = request.session['projects']
            return self.render_to_response(context)
        else:
            return redirect(target, slug=self.object.slug)

    def set_values(self):
        self.object = self.get_object()
        self.current_step = self.steps.index(self.view_name)
        return

    def set_step_complete(self):
        self.project_session['steps'][self.view_name]['state'] = 'completed'
        return

    def get_target(self):
        # Check if project has already been started.
        if self.project_session['steps'][self.view_name]['state'] == 'started':
            target = self.view_name
        elif self.project_session['steps'][self.view_name]['state'] == 'not started':  # Search backwards.
            target = self.search_target_backward(self.view_name)
        elif self.project_session['steps'][self.view_name]['state'] == 'completed':  # Search forwards.
            target = self.search_target_forward(self.view_name)
            pass
        return target

    def search_target_backward(self, view_name):
        curr_view_index = self.steps.index(view_name)
        if curr_view_index == 0:
            target = view_name
        else:
            comp_view = self.steps[curr_view_index - 1]
            comp_view_state = self.project_session['steps'][comp_view]['state']
            if comp_view_state == 'completed':
                target = view_name
            elif comp_view_state == 'started':
                target = comp_view
            else:
                target = self.search_target_backward(comp_view)
        return target

    def search_target_forward(self, view_name):
        curr_view_index = self.steps.index(view_name)
        if curr_view_index == len(self.steps) - 1:
            target = view_name
        else:
            comp_view = self.steps[curr_view_index + 1]
            comp_view_state = self.project_session['steps'][comp_view]['state']
            if comp_view_state != 'completed':
                target = comp_view
            else:
                target = self.search_target_forward(comp_view)
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
            for step in self.steps:
                request.session['projects'][f'{self.object.pk}']['steps'][step] = {
                    'state': 'not started'
                }
        self.set_project_session(request)
        return request

    def set_project_session(self, request):
        self.project_session = request.session['projects'][f'{self.object.pk}']
        return

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

    def post(self, request, *arges, **kwargs):
        self.set_values()
        self.set_project_session(request)
        self.set_step_complete()
        return redirect(self.steps[self.current_step + 1],
                        slug=self.object.slug)


class ProjectEntry(ProjectBaseView):
    template_name = 'ddm/project/entry_page.html'
    view_name = 'project-entry'

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        print(request.session['projects'])
        return redirect(self.steps[self.current_step + 1],
                        slug=self.object.slug)


class ProjectExit(ProjectBaseView):
    template_name = 'ddm/questionnaire/thankyou.html'
    view_name = 'project-exit'