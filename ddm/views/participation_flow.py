import json
import zipfile

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.template import Context, Template
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.utils.safestring import SafeString
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page

from ddm.models.core import (
    DonationBlueprint, DonationProject, Participant, QuestionnaireResponse,
    FileUploader
)
from ddm.models.logs import ExceptionLogEntry, ExceptionRaisers
from ddm.models.questions import QuestionBase


class ParticipationFlowBaseView(DetailView):
    """
    Base class for participation flow views that implements base get and post
    methods, redirects and session management.
    """
    model = DonationProject
    context_object_name = 'project'

    steps = [
        'briefing',
        'data-donation',
        'questionnaire',
        'debriefing'
    ]
    participant = None
    current_step = None
    step_name = None

    def setup(self, request, *args, **kwargs):
        """ Initialize attributes shared by all participation steps. """
        super().setup(request, *args, **kwargs)
        self._initialize_values(request)

    def get(self, request, *args, **kwargs):
        # Redirect to previous step if necessary.
        if not self.steps[self.current_step] == self.step_name:
            return redirect(self.steps[self.current_step], slug=self.object.slug)

        # Render current view.
        context = self.get_context_data(object=self.object)
        self.extra_before_render(request)
        return self.render_to_response(context)

    def post(self, request, *arges, **kwargs):
        self.set_step_completed(request)
        return redirect(self.steps[self.current_step + 1],
                        slug=self.object.slug)

    def register_project_in_session(self, request):
        if not request.session.get(self.get_session_id()):
            request.session[self.get_session_id()] = {
                'participant_id': None,
                'last_completed_step': None
            }
            request.session.modified = True
        return

    def get_session_id(self):
        """
        Return id under which project related information is stored in a
        participant's session.
        """
        return f'project-{self.object.pk}'

    def get_participant_from_session(self, request):
        """
        Gets participant from session. If participant has not yet been created,
        creates new participant and saves it to session.
        """
        participant_id = request.session[self.get_session_id()]['participant_id']
        try:
            participant = Participant.objects.get(pk=participant_id)
        except Participant.DoesNotExist:
            participant = Participant.objects.create(
                project=self.object,
                start_time=timezone.now()
            )
            request.session[self.get_session_id()]['participant_id'] = participant.id
            request.session.modified = True
        return participant

    def get_current_step_from_session(self, request):
        """
        Gets current step from information stored in participant's session.
        """
        step = request.session[self.get_session_id()]['last_completed_step']
        if step is None:
            current_step = 0
        else:
            current_step = step + 1
        return current_step

    def set_step_completed(self, request):
        """
        Updates the last_completed_step attribute in current session.
        """
        request.session[self.get_session_id()]['last_completed_step'] = self.current_step
        request.session.modified = True
        return

    def extra_before_render(self, request):
        """
        Placeholder for stage specific code executed before rendering the
        response.
        """
        pass

    def _initialize_values(self, request):
        self.object = self.get_object()
        self.register_project_in_session(request)
        self.participant = self.get_participant_from_session(request)
        self.current_step = self.get_current_step_from_session(request)
        return


class BriefingView(ParticipationFlowBaseView):
    template_name = 'ddm/public/briefing.html'
    step_name = 'briefing'

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
            request.session[self.get_session_id()]['last_completed_step'] = len(self.steps) - 2
            request.session.modified = True
            return redirect(self.steps[-1], slug=self.object.slug)
        else:
            return super().post(request, **kwargs)

    def extra_before_render(self, request):
        """ Extract URL parameters if this option has been enabled. """
        if self.object.url_parameter_enabled:
            # Only extract URL parameters on the first call of the view.
            if not self.participant.extra_data['url_param']:
                for param in self.object.get_expected_url_parameters():
                    self.participant.extra_data['url_param'][param] = request.GET.get(param, None)
                self.participant.save()
        return


@method_decorator(cache_page(0), name='dispatch')
class DataDonationView(ParticipationFlowBaseView):
    template_name = 'ddm/public/data_donation.html'
    step_name = 'data-donation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uploader_configs'] = SafeString(self.get_uploader_configs())
        context['project_id'] = self.object.pk
        return context

    def get_uploader_configs(self):
        project_uploaders = FileUploader.objects.filter(project=self.object)
        uploader_configs = [fu.get_configs() for fu in project_uploaders]
        return json.dumps(uploader_configs)

    def post(self, request, *args, **kwargs):
        super().post(request, **kwargs)
        self.process_uploads(request.FILES)
        redirect_url = reverse(self.steps[self.current_step + 1],
                               kwargs={'slug': self.object.slug})
        return HttpResponseRedirect(redirect_url)

    def process_uploads(self, files):
        try:
            file = files['post_data']
        except MultiValueDictKeyError as err:
            msg = ('Data Donation Processing Exception: Did not receive '
                   f'expected data file from client. {err}')
            ExceptionLogEntry.objects.create(
                project=self.object,
                raised_by=ExceptionRaisers.SERVER,
                message=msg
            )
            return

        if not zipfile.is_zipfile(file):
            msg = ('Data Donation Processing Exception: Data file received '
                   'from client is not a zip file.')
            ExceptionLogEntry.objects.create(
                project=self.object,
                raised_by=ExceptionRaisers.SERVER,
                message=msg
            )
            return

        # Check if zip file contains expected file.
        unzipped_file = zipfile.ZipFile(file, 'r')
        if 'ul_data.json' not in unzipped_file.namelist():
            msg = ('Data Donation Processing Exception: "ul_data.json" is not '
                   'in namelist.')
            ExceptionLogEntry.objects.create(
                project=self.object,
                raised_by=ExceptionRaisers.SERVER,
                message=msg
            )
            return

        # Process donation data.
        file_data = json.loads(unzipped_file.read('ul_data.json').decode('utf-8'))
        for upload in file_data.keys():
            blueprint_id = upload
            blueprint_data = file_data[upload]
            try:
                blueprint = DonationBlueprint.objects.get(pk=blueprint_id,
                                                          project=self.object)
            except DonationBlueprint.DoesNotExist as e:
                msg = ('Data Donation Processing Exception: Referenced '
                       f'blueprint with id={blueprint_id} does not exist for '
                       'this project.')
                ExceptionLogEntry.objects.create(
                    project=self.object,
                    raised_by=ExceptionRaisers.SERVER,
                    message=msg
                )
                return
            blueprint.process_donation(blueprint_data, self.participant)


class QuestionnaireView(ParticipationFlowBaseView):
    template_name = 'ddm/public/questionnaire.html'
    step_name = 'questionnaire'

    def setup(self, request, *args, **kwargs):
        """ Reset extra_scripts """
        super().setup(request, *args, **kwargs)
        self.extra_scripts = []

    def get(self, request, *args, **kwargs):
        """
        Skip questionnaire if no questions are defined and redirect to next step.
        Otherwise, render questionnaire.
        """
        # Redirect to previous step if necessary.
        if not self.steps[self.current_step] == self.step_name:
            return redirect(self.steps[self.current_step], slug=self.object.slug)

        context = self.get_context_data(object=self.object)
        if not len(context['q_config']) > 2:
            self.set_step_completed(request)
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
        return redirect(self.steps[self.current_step + 1],
                        slug=self.object.slug)

    def process_response(self, response):
        try:
            post_data = json.loads(response['post_data'])
        except MultiValueDictKeyError:
            msg = ('Questionnaire Post Exception: POST did not contain '
                   'expected key "post_data".')
            ExceptionLogEntry.objects.create(
                project=self.object,
                raised_by=ExceptionRaisers.SERVER,
                message=msg
            )
            return

        for question_id in post_data:
            try:
                question = QuestionBase.objects.get(pk=int(question_id))
            except QuestionBase.doesNotExist:
                msg = ('Questionnaire Post Exception:'
                       f'Question with id={question_id} does not exist.')
                ExceptionLogEntry.objects.create(
                    project=self.object,
                    raised_by=ExceptionRaisers.SERVER,
                    message=msg
                )
                continue
            except ValueError:
                msg = ('Questionnaire Post Exception: Received invalid '
                       f'question_id ({question_id}) in questionnaire '
                       f'post_data.')
                ExceptionLogEntry.objects.create(
                    project=self.object,
                    raised_by=ExceptionRaisers.SERVER,
                    message=msg
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


class DebriefingView(ParticipationFlowBaseView):
    template_name = 'ddm/public/debriefing.html'
    step_name = 'debriefing'

    def get_context_data(self, **kwargs):
        """ Inject url parameters in redirect target. """
        context = super().get_context_data(**kwargs)
        if self.object.redirect_enabled:
            template = Template(self.object.redirect_target)
            template_context = self.participant.extra_data['url_param']
            template_context['ddm_participant_id'] = self.participant.pk
            template_context['ddm_project_id'] = self.object.pk
            context['redirect_target'] = template.render(Context(template_context))
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
