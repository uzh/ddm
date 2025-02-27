import json
import zipfile
from json import JSONDecodeError

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.utils.safestring import SafeString
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page

from ddm.core.utils.user_content.template import render_user_content
from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.logging.utils import log_server_exception
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.questionnaire.services import save_questionnaire_to_db


def get_participation_session_id(project):
    """
    Return id under which project related information is stored in a
    participant's session.
    """
    return f'project-{project.pk}'


def create_participation_session(request, project):
    """ Creates a new participation session if none does yet exist. """
    session_id = get_participation_session_id(project)

    if not request.session.get(session_id):
        participant = Participant.objects.create(
            project=project,
            start_time=timezone.now()
        )
        request.session[session_id] = {'participant_id': participant.id}
        request.session.modified = True
    return


class ParticipationFlowBaseView(DetailView):
    """
    Base class for participation flow views that implements base get and post
    methods, redirects and session management.
    """
    model = DonationProject
    context_object_name = 'project'

    steps = [
        'ddm_participation:briefing',
        'ddm_participation:datadonation',
        'ddm_participation:questionnaire',
        'ddm_participation:debriefing'
    ]
    participant = None
    current_step = None
    step_name = None

    def setup(self, request, *args, **kwargs):
        """ Initialize attributes shared by all participation steps. """
        super().setup(request, *args, **kwargs)
        self._initialize_values(request)

    def get(self, request, *args, **kwargs):
        # Check if project is active.
        if not self.object.active:
            return redirect(
                'ddm_participation:project_inactive', slug=self.object.slug)

        # Redirect to previous step if necessary.
        if not self.steps[self.current_step] == self.step_name:
            return redirect(self.steps[self.current_step], slug=self.object.slug)

        # Render current view.
        context = self.get_context_data(object=self.object)
        self.extra_before_render(request)
        return self.render_to_response(context)

    def post(self, request, *arges, **kwargs):
        # Account for 'page back' action in browser
        if self.steps[self.current_step] == self.step_name:
            self.set_step_completed()
            return redirect(
                self.steps[self.current_step + 1], slug=self.object.slug)
        else:
            return redirect(
                self.steps[self.current_step], slug=self.object.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'default_header_left': getattr(settings, 'DDM_DEFAULT_HEADER_IMG_LEFT', None),
            'default_header_right': getattr(settings, 'DDM_DEFAULT_HEADER_IMG_RIGHT', None),
        })
        return context

    def get_participant_from_session(self, request):
        """
        Gets participant from session. If participant has not yet been created,
        creates new participant and saves it to session.
        """
        session_id = get_participation_session_id(self.object)
        participant_id = request.session[session_id]['participant_id']
        try:
            participant = Participant.objects.get(pk=participant_id)
        except Participant.DoesNotExist:
            participant = Participant.objects.create(
                project=self.object,
                start_time=timezone.now()
            )
            request.session[session_id]['participant_id'] = participant.id
            request.session.modified = True
        return participant

    @staticmethod
    def get_current_step_from_participant(participant):
        """
        Gets current step from information stored in participant's session.
        """
        step = participant.current_step
        if step is None:
            current_step = 0
            participant.current_step = 0
            participant.save()
        else:
            current_step = step
        return current_step

    def set_step_completed(self):
        """
        Updates the last_completed_step attribute in current session.
        """
        self.participant.current_step += 1
        self.participant.save()
        return

    def extra_before_render(self, request):
        """
        Placeholder for stage specific code executed before rendering the
        response.
        """
        pass

    def _initialize_values(self, request):
        self.object = self.get_object()
        create_participation_session(request, self.object)
        self.participant = self.get_participant_from_session(request)
        self.current_step = self.get_current_step_from_participant(self.participant)
        return


def participation_redirect_view(request, slug):
    """
    Redirect user to briefing page if url does not contain a step indicator.
    """
    redirect_url = reverse('ddm_participation:briefing', args=[slug])
    query_string = request.META.get('QUERY_STRING', '')
    return redirect(f'{redirect_url}?{query_string}')


class BriefingView(ParticipationFlowBaseView):
    template_name = 'ddm_participation/briefing.html'
    step_name = 'ddm_participation:briefing'

    def post(self, request, *args, **kwargs):
        """
        Checks whether participant has provided briefing consent to continue with
        the study. If briefing consent is not given, redirects to end page.
        If briefing consent is not within the expected values, the briefing page
        is again returned with a form error.
        """
        # Check briefing consent if enabled for project.
        if self.get_object().briefing_consent_enabled:
            return self.check_consent(request, **kwargs)

        return super().post(request, **kwargs)

    def check_consent(self, request, **kwargs):
        """
        Checks whether post data contains information on briefing consent.
        Renders briefing view with error message if consent information is invalid.
        Renders debriefing view if no consent has been given.
        Renders next step if consent has been given.
        """
        # Check that answer has been provided and is valid.
        consent = request.POST.get('briefing_consent', None)
        if consent not in ['0', '1']:
            # Render briefing view again with error message.
            context = self.get_context_data(object=self.object)
            context.update({'briefing_error': True})
            return self.render_to_response(context)

        # Save consent to participant data.
        self.participant.extra_data['briefing_consent'] = consent
        self.participant.save()

        if consent == '0':
            # Redirect to debriefing page.
            self.participant.current_step = len(self.steps) - 1
            self.participant.save()
            return redirect(self.steps[-1], slug=self.object.slug)
        else:
            return super().post(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.url_parameter_enabled:
            self.extract_url_parameter()
        context['participant'] = self.participant
        participant_info = self.participant.get_context_data()
        context['briefing'] = render_user_content(self.object.briefing_text, participant_info)
        return context

    def extract_url_parameter(self):
        """
        Extract URL parameters on first call of the view and save to
        participant.extra_data.
        """
        if not self.participant.extra_data['url_param']:
            for param in self.object.get_expected_url_parameters():
                self.participant.extra_data['url_param'][param] = self.request.GET.get(param, None)
            self.participant.save()
        return


@method_decorator(cache_page(0), name='dispatch')
class DataDonationView(ParticipationFlowBaseView):
    template_name = 'ddm_participation/data_donation.html'
    step_name = 'ddm_participation:datadonation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uploader_configs'] = SafeString(self.get_uploader_configs())
        context['project_url_id'] = self.object.url_id
        return context

    def get_uploader_configs(self):
        project_uploaders = FileUploader.objects.filter(project=self.object)
        uploader_configs = [fu.get_configs(self.participant.get_context_data()) for fu in project_uploaders]
        return json.dumps(uploader_configs)

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)  # TODO: Check if this is obsolete
        self.process_uploads(request.FILES)
        redirect_url = reverse(self.steps[self.current_step + 1], kwargs={'slug': self.object.slug})
        return HttpResponseRedirect(redirect_url)

    def process_uploads(self, files):
        try:
            file = files['post_data']
        except (MultiValueDictKeyError, KeyError) as e:
            msg = ('Data Donation Processing Exception: Did not receive '
                   f'expected data file from client. {e}')
            log_server_exception(self.object, msg)
            return

        if not zipfile.is_zipfile(file):
            msg = ('Data Donation Processing Exception: Data file received '
                   'from client is not a zip file.')
            log_server_exception(self.object, msg)
            return

        # Check if zip file contains expected file.
        unzipped_file = zipfile.ZipFile(file, 'r')
        if 'ul_data.json' not in unzipped_file.namelist():
            msg = 'Data Donation Processing Exception: "ul_data.json" is not in namelist.'
            log_server_exception(self.object, msg)
            return

        # Process donation data.
        try:
            file_data = json.loads(unzipped_file.read('ul_data.json').decode('utf-8'))
        except UnicodeDecodeError:
            try:
                file_data = json.loads(unzipped_file.read('ul_data.json').decode('latin-1'))
            except ValueError:
                msg = 'Donated data could not be decoded - tried both utf-8 and latin-1 decoding.'
                log_server_exception(self.object, msg)
                return
        except JSONDecodeError:
            msg = 'JSON decode error in donated data.'
            log_server_exception(self.object, msg)
            return

        for upload in file_data.keys():
            blueprint_id = upload
            blueprint_data = file_data[upload]
            try:
                blueprint = DonationBlueprint.objects.get(pk=blueprint_id,
                                                          project=self.object)
            except DonationBlueprint.DoesNotExist:
                msg = ('Data Donation Processing Exception: Referenced '
                       f'blueprint with id={blueprint_id} does not exist for '
                       'this project.')
                log_server_exception(self.object, msg)
                return
            blueprint.process_donation(blueprint_data, self.participant)


class QuestionnaireView(ParticipationFlowBaseView):
    template_name = 'ddm_participation/questionnaire.html'
    step_name = 'ddm_participation:questionnaire'

    def setup(self, request, *args, **kwargs):
        """ Reset extra_scripts """
        super().setup(request, *args, **kwargs)
        self.extra_scripts = []

    def get(self, request, *args, **kwargs):
        """
        Skip questionnaire if no questions are defined and redirect to next step.
        Otherwise, render questionnaire.
        """
        # Check if project is active.
        if not self.object.active:
            return redirect(
                'ddm_participation:project_inactive', slug=self.object.slug)

        # Redirect to previous step if necessary.
        if not self.steps[self.current_step] == self.step_name:
            return redirect(self.steps[self.current_step], slug=self.object.slug)

        context = self.get_context_data(object=self.object)
        if not len(context['q_config']) > 2:
            self.set_step_completed()
            return redirect(self.steps[self.current_step + 1],
                            slug=self.object.slug)
        else:
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_config = self.object.get_questionnaire_config(self.participant, self)
        context['q_config'] = json.dumps(question_config)
        context['extra_scripts'] = set(self.extra_scripts)
        return context

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        self.process_response(request.POST)
        return redirect(self.steps[self.current_step + 1], slug=self.object.slug)

    def process_response(self, response):
        try:
            post_data = json.loads(response['post_data'])
        except MultiValueDictKeyError:
            msg = ('Questionnaire Post Exception: POST did not contain '
                   'expected key "post_data".')
            log_server_exception(self.object, msg)
            return

        save_questionnaire_to_db(post_data, self.object, self.participant)
        return


class DebriefingView(ParticipationFlowBaseView):
    template_name = 'ddm_participation/debriefing.html'
    step_name = 'ddm_participation:debriefing'

    def get_context_data(self, **kwargs):
        """ Inject url parameters in redirect target. """
        context = super().get_context_data(**kwargs)

        template_context = self.participant.get_context_data()
        template_context.update({'project_id': self.object.url_id})
        context['debriefing'] = render_user_content(self.object.debriefing_text, template_context)

        if self.object.redirect_enabled:
            context['redirect_target'] = render_user_content(self.object.redirect_target, template_context)
        else:
            context['redirect_target'] = None
        return context

    def extra_before_render(self, request):
        """Set step to completed and update participant information."""
        if not self.participant.completed:
            self.participant.end_time = timezone.now()
            self.participant.completed = True
            self.participant.save()
        return


class ContinuationView(DetailView):
    """
    Enables the continuation of the study at a later stage.
    Retrieves the session for a participant id passed as a URL parameter (?p=)
    and redirects to the last initiated stage of the study by the given
    participant.
    """
    model = DonationProject
    context_object_name = 'project'
    template_name = 'ddm_participation/continuation_not_found.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        participant_id = request.GET.get('p', None)
        try:
            participant = Participant.objects.get(external_id=participant_id)
        except Participant.DoesNotExist:
            # render continuation failed view with option to start new
            return self.render_to_response(context)

        self.initialize_session(request, participant.pk)
        return redirect(ParticipationFlowBaseView.steps[0], slug=self.object.slug)

    def initialize_session(self, request, participant_id):
        request.session[f'project-{self.object.pk}'] = {
            'participant_id': participant_id
        }
        request.session.modified = True
        return


class ProjectInactiveView(TemplateView):
    template_name = 'ddm_participation/project_inactive.html'
