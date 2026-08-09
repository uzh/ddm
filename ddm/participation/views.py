import json
import zipfile
from json import JSONDecodeError
from typing import Any

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from ddm.core.utils.user_content.template import render_user_content
from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.logging.utils import log_server_exception
from ddm.participation.models import Participant
from ddm.participation.services import (
    QuestionnaireConfigService,
    UploaderConfigService,
)
from ddm.projects.models import DonationProject
from ddm.projects.service import (
    get_donation_variables,
    get_participant_variables,
    get_url_parameters,
)
from ddm.questionnaire.services import save_questionnaire_response_to_db


def get_participation_session_id(project: DonationProject) -> str:
    """
    Return id under which project related information is stored in a
    participant's session.
    """
    return f"project-{project.pk}"


def create_participation_session(
    request: HttpRequest, project: DonationProject
) -> None:
    """Creates a new participation session if none does yet exist."""
    session_id = get_participation_session_id(project)

    if not request.session.get(session_id):
        participant = Participant.objects.create(
            project=project, start_time=timezone.now()
        )
        request.session[session_id] = {"participant_id": participant.id}
        request.session.modified = True


def has_valid_zip_paths(zip_file: zipfile.ZipFile) -> bool:
    """Check that ZIP file doesn't contain path traversal attempts.

    Rejects ZIP files containing entries with:
    - Empty filenames
    - Absolute paths (starting with /)
    - Parent directory references (..)

    Note: This is a defensive measure - the current code only reads specific
    files by name and doesn't extract to disk, but this validation
    protects against future code changes and aids security audits.
    """
    for name in zip_file.namelist():
        if not name or name.startswith("/") or ".." in name:
            return False
    return True


class ParticipationFlowBaseView(DetailView):
    """
    Base class for participation flow views that implements base get and post
    methods, redirects and session management.
    """

    model = DonationProject
    context_object_name = "project"

    steps = [
        "ddm_participation:briefing",
        "ddm_participation:datadonation",
        "ddm_participation:questionnaire",
        "ddm_participation:debriefing",
    ]
    participant = None
    current_step = None
    step_name = None

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Initialize attributes shared by all participation steps."""
        super().setup(request, *args, **kwargs)
        self._initialize_values(request)

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        if not self.object.active:
            return redirect(self.inactive_url())

        # Redirect to previous step if necessary.
        if self.steps[self.current_step] != self.step_name:
            return redirect(self.current_step_url())

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data(object=self.object)
        self.extra_before_render(request)
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Account for 'page back' action in browser
        if self.steps[self.current_step] == self.step_name:
            self.set_step_completed()
            return redirect(self.next_step_url())
        return redirect(self.current_step_url())

    def current_step_url(self) -> str:
        return reverse(self.steps[self.current_step], kwargs={"slug": self.object.slug})

    def next_step_url(self) -> str:
        return reverse(
            self.steps[self.current_step + 1], kwargs={"slug": self.object.slug}
        )

    def inactive_url(self) -> str:
        return reverse(
            "ddm_participation:project_inactive", kwargs={"slug": self.object.slug}
        )

    def end_page_url(self) -> str:
        return reverse(self.steps[-1], kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "default_header_left": getattr(
                    settings, "DDM_DEFAULT_HEADER_IMG_LEFT", None
                ),
                "default_header_right": getattr(
                    settings, "DDM_DEFAULT_HEADER_IMG_RIGHT", None
                ),
            }
        )
        return context

    def get_participant_from_session(self, request: HttpRequest) -> Participant:
        """Gets participant from session.

        If participant does not exist, creates new participant and saves it to
        session.
        """
        session_id = get_participation_session_id(self.object)
        participant_id = request.session[session_id]["participant_id"]

        participant, created = Participant.objects.get_or_create(
            pk=participant_id,
            defaults={"project": self.object, "start_time": timezone.now()},
        )
        if created:
            request.session[session_id]["participant_id"] = participant.id
            request.session.modified = True

        return participant

    @staticmethod
    def get_current_step_from_participant(participant: Participant) -> int:
        """Gets current step from information stored in participant's session."""

        step = participant.current_step
        if step is None:
            current_step = 0
            participant.current_step = 0
            participant.save()
        else:
            current_step = step
        return current_step

    def set_step_completed(self) -> None:
        """Updates the last_completed_step attribute in current session."""

        self.participant.current_step += 1
        self.participant.save()

    def extra_before_render(self, request: HttpRequest) -> None:
        """
        Placeholder for stage specific code executed before rendering the
        response.
        """

    def _initialize_values(self, request: HttpRequest) -> None:
        self.object = self.get_object()
        create_participation_session(request, self.object)
        self.participant = self.get_participant_from_session(request)
        self.current_step = self.get_current_step_from_participant(self.participant)


def participation_redirect_view(
    request: HttpRequest, slug: str
) -> HttpResponseRedirect:
    """Redirect user to briefing page if url does not contain a step indicator."""

    redirect_url = reverse("ddm_participation:briefing", args=[slug])
    query_string = request.META.get("QUERY_STRING", "")
    return redirect(f"{redirect_url}?{query_string}")


class BriefingView(ParticipationFlowBaseView):
    template_name = "ddm_participation/briefing.html"
    step_name = "ddm_participation:briefing"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if self.object.url_parameter_enabled:
            self.extract_url_parameter()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Checks whether participant has provided briefing consent.

        If briefing consent is not given, redirects to end page.
        If briefing consent is not within the expected values, the briefing page
        is again returned with a form error.
        """
        # Check briefing consent if enabled for project.
        if self.get_object().briefing_consent_enabled:
            return self.check_consent(request, **kwargs)

        return super().post(request, **kwargs)

    def check_consent(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Checks whether post data contains information on briefing consent.

        Renders briefing view with error message if consent information is invalid.
        Renders debriefing view if no consent has been given.
        Renders next step if consent has been given.
        """
        # Check that answer has been provided and is valid.
        consent = request.POST.get("briefing_consent")
        if consent not in {"0", "1"}:
            # Render briefing view again with error message.
            context = self.get_context_data(object=self.object)
            context["briefing_error"] = True
            return self.render_to_response(context)

        # Save consent to participant data.
        self.participant.extra_data["briefing_consent"] = consent

        if consent == "0":
            # Redirect to debriefing page.
            self.participant.current_step = len(self.steps) - 1
            self.participant.save()
            return redirect(self.end_page_url())

        self.participant.save()
        return super().post(request, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        participant_info = self.participant.get_context_data()
        context.update(
            {
                "participant": self.participant,
                "briefing": render_user_content(
                    self.object.briefing_text, participant_info
                ),
            }
        )
        return context

    def extract_url_parameter(self) -> None:
        """Extract URL parameters on first call of the view

        Saves parameters to participant.url_parameter.
        """
        if not self.participant.url_parameter:
            for param in self.object.get_expected_url_parameters():
                self.participant.url_parameter[param] = self.request.GET.get(
                    param, None
                )
            self.participant.save()


@method_decorator(cache_page(0), name="dispatch")
class DataDonationView(ParticipationFlowBaseView):
    template_name = "ddm_participation/data_donation.html"
    step_name = "ddm_participation:datadonation"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "uploader_configs": self.get_uploader_configs(),
                "project_url_id": self.object.url_id,
                "custom_translations": self.object.custom_uploader_translations,
            }
        )
        return context

    def get_uploader_configs(self) -> list:
        project_uploaders = FileUploader.objects.filter(project=self.object)
        return UploaderConfigService.create_configs(project_uploaders, self.participant)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        super().post(request, **kwargs)
        self.process_uploads(request.FILES)
        return HttpResponseRedirect(self.post_redirect_url())

    def post_redirect_url(self) -> str:
        return reverse(
            self.steps[self.current_step + 1], kwargs={"slug": self.object.slug}
        )

    def process_uploads(self, files: dict[str, UploadedFile]) -> None:
        file = self._get_uploaded_file(files)
        if file is None:
            return

        unzipped_file = self._get_validated_zip(file)
        if unzipped_file is None:
            return

        file_data = self._load_donation_json(unzipped_file)
        if file_data is None:
            return

        self.process_blueprints(file_data)

    def _log_error(self, msg: str) -> None:
        log_server_exception(self.object, f"Data Donation Processing Exception: {msg}")

    def _get_uploaded_file(self, files: dict[str, UploadedFile]) -> UploadedFile | None:
        try:
            return files["post_data"]
        except (MultiValueDictKeyError, KeyError) as e:
            self._log_error(
                f"Did not receive expected data file from client"
                f" - missing key 'post_data'. {e}"
            )
            return None

    def _get_validated_zip(self, file: UploadedFile) -> zipfile.ZipFile | None:
        if not zipfile.is_zipfile(file):
            self._log_error("File received in post_data is not a zip file.")
            return None

        unzipped_file = zipfile.ZipFile(file, "r")

        if not has_valid_zip_paths(unzipped_file):
            self._log_error("ZIP file contains invalid file paths.")
            return None

        if "data_donation.json" not in unzipped_file.namelist():
            self._log_error(
                "ZIP file does not contain expected 'data_donation.json' file."
            )
            return None

        return unzipped_file

    def _decode_bytes(self, raw_bytes: bytes) -> str | None:
        for encoding in ("utf-8", "latin-1"):
            try:
                return raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        self._log_error(
            "Donated data could not be decoded - tried utf-8 and latin-1 decoding."
        )
        return None

    def _load_donation_json(self, unzipped_file: zipfile.ZipFile) -> dict | None:
        raw_bytes = unzipped_file.read("data_donation.json")

        text = self._decode_bytes(raw_bytes)
        if text is None:
            return None

        try:
            return json.loads(text)
        except JSONDecodeError:
            self._log_error("JSON decode error in donated data.")
            return None

    def process_blueprints(self, file_data: dict[str, dict]) -> None:
        """Process each blueprint's donation data.

        Args:
            file_data: mapping of blueprint_id (str) -> blueprint_data (dict),
                as parsed from the uploaded data_donation.json.
        """
        for blueprint_id, blueprint_data in file_data.items():
            try:
                blueprint = DonationBlueprint.objects.get(
                    pk=blueprint_id, project=self.object
                )
            except DonationBlueprint.DoesNotExist:
                self._log_error(
                    f"Referenced blueprint with id={blueprint_id} does not exist "
                    "for this project."
                )
                return
            blueprint.process_donation(blueprint_data, self.participant)


class QuestionnaireView(ParticipationFlowBaseView):
    template_name = "ddm_participation/questionnaire.html"
    step_name = "ddm_participation:questionnaire"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extra_scripts = []

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Skip questionnaire if no questions are defined.

        Redirects to next step if questionnaire is skipped.
        Otherwise, render questionnaire.
        """
        context = self.get_context_data(object=self.object)
        if not context["q_config"]:
            self.set_step_completed()
            return redirect(self.next_step_url())
        return self.render_to_response(context)

    def get_extra_variables(self) -> dict:
        """Get url parameter-, participant- and donation-variables from participant.

        Returns a dictionary holding variable_name: participant_value pairs to
        be sent to the questionnaire app. This is needed to evaluate filter
        conditions.
        """
        variables = {}
        variables.update(get_url_parameters(self.object, self.participant))
        variables.update(get_participant_variables(self.participant))
        variables.update(get_donation_variables(self.participant))
        return variables

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        config_service = QuestionnaireConfigService(self.object, self.participant)
        context.update(
            {
                "q_config": config_service.create_questionnaire_config(),
                "filter_config": config_service.create_filter_config(),
                "extra_scripts": set(self.extra_scripts),
                "extra_variables": self.get_extra_variables(),
            }
        )
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        super().post(request, **kwargs)
        self.process_response(request.POST)
        return redirect(self.post_redirect_url())

    def post_redirect_url(self) -> str:
        return reverse(
            self.steps[self.current_step + 1], kwargs={"slug": self.object.slug}
        )

    def process_response(self, response: dict) -> None:
        try:
            post_data = json.loads(response["post_data"])
        except MultiValueDictKeyError:
            msg = (
                "Questionnaire Post Exception: POST did not contain "
                'expected key "post_data".'
            )
            log_server_exception(self.object, msg)
            return
        responses = post_data.get("responses", None)
        questionnaire_config = post_data.get("questionnaire_config", None)
        save_questionnaire_response_to_db(
            responses, self.object, self.participant, questionnaire_config
        )
        return


class DebriefingView(ParticipationFlowBaseView):
    template_name = "ddm_participation/debriefing.html"
    step_name = "ddm_participation:debriefing"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Inject url parameters in redirect target."""
        context = super().get_context_data(**kwargs)

        template_context = self.participant.get_context_data()
        template_context.update({"project_id": self.object.url_id})

        context.update(
            {
                "debriefing": self.render_debriefing_text(template_context),
                "redirect_target": self.render_redirect_url(template_context),
            }
        )
        return context

    def render_debriefing_text(self, template_context: dict | None = None) -> str:
        return render_user_content(self.object.debriefing_text, template_context)

    def render_redirect_url(self, template_context: dict | None = None) -> str | None:
        if not self.object.redirect_enabled:
            return None
        return render_user_content(self.object.redirect_target, template_context)

    def extra_before_render(self, request: HttpRequest) -> None:
        """Set step to completed and update participant information."""
        if not self.participant.completed:
            self.participant.end_time = timezone.now()
            self.participant.completed = True
            self.participant.save()


class ContinuationView(DetailView):
    """
    Enables the continuation of the study at a later stage.
    Retrieves the session for a participant id passed as a URL parameter (?p=)
    and redirects to the last initiated stage of the study by the given
    participant.
    """

    model = DonationProject
    context_object_name = "project"
    template_name = "ddm_participation/continuation_not_found.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        participant_id = request.GET.get("p", None)
        try:
            participant = Participant.objects.get(external_id=participant_id)
        except Participant.DoesNotExist:
            # render continuation failed view with option to start new
            return self.render_to_response(context)

        self.initialize_session(request, participant.pk)
        return redirect(ParticipationFlowBaseView.steps[0], slug=self.object.slug)

    def initialize_session(self, request: HttpRequest, participant_id: str) -> None:
        request.session[f"project-{self.object.pk}"] = {
            "participant_id": participant_id
        }
        request.session.modified = True


class ProjectInactiveView(TemplateView):
    template_name = "ddm_participation/project_inactive.html"


class ProjectThemeView(DetailView):
    """Serves a project's primary/background color overrides as CSS.

    Served as an actual stylesheet response (loaded via <link>) to be compliant
    with strict Content-Security-Policies.

    The <link> is requested with a `?v=<theme_version>` query parameter
    (see DonationProject.theme_version) derived from the current colors, so
    changing a color changes the URL. That lets this response be cached
    aggressively without going stale: a color change is always served from
    a new URL rather than an old cached response.
    """

    model = DonationProject
    context_object_name = "project"
    content_type = "text/css"
    template_name = "ddm_participation/project_theme.css"

    def render_to_response(self, context: dict, **kwargs) -> HttpResponse:
        response = super().render_to_response(context, **kwargs)
        response["Cache-Control"] = "public, max-age=31536000, immutable"
        return response
