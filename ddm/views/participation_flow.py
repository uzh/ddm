import json
import zipfile

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.utils.safestring import SafeString
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page

from ddm.models import (
    DonationProject, Participant, DonationBlueprint, ZippedBlueprint,
    QuestionBase, QuestionnaireResponse, DataDonation
)

import logging
logger = logging.getLogger(__name__)


class ParticipationFlowBaseView(DetailView):
    """
    Base class for participation flow views that implements base get and post
    methods, redirects and session management.
    """
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
            request.session.modified = True
            return self.render_to_response(context)
        else:
            return redirect(target, slug=self.object.slug)

    def initialize_values(self, request):
        self.object = self.get_object()
        self.current_step = self.steps.index(self.view_name)

        # Initialize or read session data.
        self.register_project_in_session(request)
        request.session.modified = True
        self.project_session = request.session['projects'][f'{self.object.pk}']

        # Save shortcuts to session information.
        self.get_participant()
        self.state = self.project_session['steps'][self.view_name]['state']
        return

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
        return

    def get_participant(self):
        """
        Gets participant from session. If participant has not yet been created,
        creates new participant and saves it to session.
        """
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
        """
        Determines which view of the participation flow should be rendered next.
        Needed to redirect participants to the correct step in the flow.
        Also needed to determine redirects if a participant enters the flow in
        a step that has already been concluded or not yet started.
        """
        def search_backward(project_session, view_name):
            current_step_index = ParticipationFlowBaseView.steps.index(view_name)
            if current_step_index == 0:
                next_target = view_name
            else:
                next_step = ParticipationFlowBaseView.steps[current_step_index - 1]
                next_step_state = project_session['steps'][next_step]['state']
                if next_step_state == 'completed':
                    next_target = view_name
                elif next_step_state == 'started':
                    next_target = next_step
                else:
                    next_target = search_backward(project_session, next_step)
            return next_target

        def search_forward(project_session, view_name):
            current_step_index = ParticipationFlowBaseView.steps.index(view_name)
            if current_step_index == len(ParticipationFlowBaseView.steps) - 1:
                next_target = view_name
            else:
                next_step = ParticipationFlowBaseView.steps[current_step_index + 1]
                next_step_state = project_session['steps'][next_step]['state']
                if next_step_state != 'completed':
                    next_target = next_step
                else:
                    next_target = search_forward(project_session, next_step)
            return next_target

        if self.state == 'started':
            target = self.view_name
        elif self.state == 'not started':
            target = search_backward(self.project_session, self.view_name)
        elif self.state == 'completed':
            target = search_forward(self.project_session, self.view_name)
        else:
            target = None
        return target

    def set_step_complete(self):
        """ Sets a step to 'completed' in the session. """
        self.project_session['steps'][self.view_name]['state'] = 'completed'
        return

    def post(self, request, *arges, **kwargs):
        self.initialize_values(request)
        self.project_session['steps'][self.view_name]['state'] = 'completed'
        request.session.modified = True
        return redirect(self.steps[self.current_step + 1],
                        slug=self.object.slug)


class EntryView(ParticipationFlowBaseView):
    template_name = 'ddm/public/entry_page.html'
    view_name = 'project-entry'

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        return redirect(self.steps[self.current_step + 1],
                        slug=self.object.slug)


@method_decorator(cache_page(0), name='dispatch')
class DataDonationView(ParticipationFlowBaseView):
    template_name = 'ddm/public/data_donation.html'
    view_name = 'data-donation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ul_configs'] = SafeString(self.get_blueprint_configs())
        return context

    def get_blueprint_configs(self):
        blueprint_configs = []

        zip_blueprints = ZippedBlueprint.objects.filter(project=self.object)
        for blueprint in zip_blueprints:
            blueprint_configs.append({
                'ul_type': 'zip',
                'name': blueprint.name,
                'blueprints': blueprint.get_configs(),
                'instructions': blueprint.get_instructions()
            })

        blueprints = DonationBlueprint.objects.filter(
            project=self.object,
            zip_blueprint__isnull=True)
        for blueprint in blueprints:
            blueprint_configs.append({
                'ul_type': 'singlefile',
                'name': blueprint.name,
                'blueprints': [blueprint.get_config()],
                'instructions': blueprint.get_instructions()
            })
        return json.dumps(blueprint_configs)

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        self.process_uploads(request.FILES)
        redirect_url = reverse(self.steps[self.current_step + 1],
                               kwargs={'slug': self.object.slug})
        return HttpResponseRedirect(redirect_url)

    def process_uploads(self, files):
        # Check if expected file in request.FILES.
        try:
            file = files['post_data']
        except MultiValueDictKeyError as err:
            logger.error(f'Did not receive expected file. {err}')
            return

        # Check if file is a zip file.
        if not zipfile.is_zipfile(file):
            logger.error('Received file is not a zip file.')
            return

        # Check if zip file contains expected file.
        unzipped_file = zipfile.ZipFile(file, 'r')
        if 'ul_data.json' not in unzipped_file.namelist():
            logger.error('"ul_data.json" is not in namelist.')
            return

        # Process donation data.
        file_data = json.loads(unzipped_file.read('ul_data.json').decode('utf-8'))
        for upload in file_data.keys():
            blueprint_id = upload
            blueprint_data = file_data[upload]
            try:
                blueprint = DonationBlueprint.objects.get(pk=blueprint_id)
            except DonationBlueprint.DoesNotExist as e:
                logger.error(
                    f'{e} – Donation blueprint with id={blueprint_id} does not exist')
                return
            blueprint.process_donation(blueprint_data, self.participant)


class QuestionnaireView(ParticipationFlowBaseView):
    template_name = 'ddm/public/questionnaire.html'
    view_name = 'questionnaire'

    def render_to_response(self, context, **response_kwargs):
        # Check if there are any questions to display.
        if not len(context['q_config']) > 2:
            self.project_session['steps'][self.view_name]['state'] = 'completed'
            current_step = self.steps.index(self.view_name)
            target = self.steps[current_step + 1]
            return redirect(target, slug=self.object.slug)
        else:
            return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_config = self.get_question_config()
        context['q_config'] = json.dumps(question_config)
        return context

    def get_question_config(self):
        question_config = []
        questions = QuestionBase.objects.filter(project=self.object)
        for question in questions:
            try:
                donation = DataDonation.objects.get(
                    blueprint=question.blueprint,
                    participant=self.participant
                )
                if donation.data:
                    question_config.append(question.get_config(self.participant))
            except ObjectDoesNotExist:
                logger.error(
                    f'No donation found for participant {self.participant.pk} '
                    f'and blueprint {question.blueprint.pk}.'
                )
        return question_config

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        self.process_response(request.POST)
        redirect_url = reverse(self.steps[self.current_step + 1],
                               kwargs={'slug': self.object.slug})
        return HttpResponseRedirect(redirect_url)

    def process_response(self, response):
        try:
            post_data = json.loads(response['post_data'])
        except MultiValueDictKeyError:
            logger.error(f'POST did not contain expected key "post_data".')
            return

        for question_id in post_data:
            try:
                question = QuestionBase.objects.get(pk=int(question_id))
            except QuestionBase.doesNotExist:
                logger.error(f'Question with id={question_id} does not exist.')
                continue
            except ValueError:
                logger.error(
                    f'Received invalid question_id ({question_id}) in '
                    f'questionnaire post_data.'
                )
                continue
            question.validate_response(post_data[question_id])

        self.save_response(response)

    def save_response(self, response):
        QuestionnaireResponse.objects.create(
            project=self.object,
            participant=self.participant,
            time_submitted=timezone.now(),
            data=response
        )


class ExitView(ParticipationFlowBaseView):
    template_name = 'ddm/public/end.html'
    view_name = 'project-exit'

    def post(self, request, *args, **kwargs):
        self.initialize_values(request)
        self.project_session['steps'][self.view_name]['state'] = 'completed'
        request.session.modified = True
        return self.get(request, *args, **kwargs)
