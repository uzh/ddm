import json
import zipfile
from json import JSONDecodeError
from typing import Any

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
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

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Check if project is active.
        if not self.object.active:
            return redirect("ddm_participation:project_inactive", slug=self.object.slug)

        # Redirect to previous step if necessary.
        if self.steps[self.current_step] != self.step_name:
            return redirect(self.steps[self.current_step], slug=self.object.slug)

        # Render current view.
        context = self.get_context_data(object=self.object)
        self.extra_before_render(request)
        return self.render_to_response(context)

    def post(self, request: HttpRequest, *arges, **kwargs) -> HttpResponse:
        # Account for 'page back' action in browser
        if self.steps[self.current_step] == self.step_name:
            self.set_step_completed()
            return redirect(self.steps[self.current_step + 1], slug=self.object.slug)
        return redirect(self.steps[self.current_step], slug=self.object.slug)

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

        If participant has not yet been created, creates new participant and
        saves it to session.
        """
        session_id = get_participation_session_id(self.object)
        participant_id = request.session[session_id]["participant_id"]
        try:
            participant = Participant.objects.get(pk=participant_id)
        except Participant.DoesNotExist:
            participant = Participant.objects.create(
                project=self.object, start_time=timezone.now()
            )
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
        consent = request.POST.get("briefing_consent", None)
        if consent not in ["0", "1"]:
            # Render briefing view again with error message.
            context = self.get_context_data(object=self.object)
            context.update({"briefing_error": True})
            return self.render_to_response(context)

        # Save consent to participant data.
        self.participant.extra_data["briefing_consent"] = consent
        self.participant.save()

        if consent == "0":
            # Redirect to debriefing page.
            self.participant.current_step = len(self.steps) - 1
            self.participant.save()
            return redirect(self.steps[-1], slug=self.object.slug)
        return super().post(request, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.object.url_parameter_enabled:
            self.extract_url_parameter()
        context["participant"] = self.participant
        participant_info = self.participant.get_context_data()
        context["briefing"] = render_user_content(
            self.object.briefing_text, participant_info
        )
        return context

    def extract_url_parameter(self) -> None:
        """Extract URL parameters on first call of the view

        Saves parameters to participant.extra_data.
        """
        if not self.participant.extra_data["url_param"]:
            for param in self.object.get_expected_url_parameters():
                self.participant.extra_data["url_param"][param] = self.request.GET.get(
                    param, None
                )
            self.participant.save()


@method_decorator(cache_page(0), name="dispatch")
class DataDonationView(ParticipationFlowBaseView):
    template_name = "ddm_participation/data_donation.html"
    step_name = "ddm_participation:datadonation"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["uploader_configs"] = self.get_uploader_configs()
        context["project_url_id"] = self.object.url_id
        context["custom_translations"] = self.object.custom_uploader_translations
        return context

    def get_uploader_configs(self) -> list:
        project_uploaders = FileUploader.objects.filter(project=self.object)
        return UploaderConfigService.create_configs(project_uploaders, self.participant)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        super().post(request, **kwargs)
        self.process_uploads(request.FILES)
        redirect_url = reverse(
            self.steps[self.current_step + 1], kwargs={"slug": self.object.slug}
        )
        return HttpResponseRedirect(redirect_url)

    # TODO: Refactor function to simplify.
    def process_uploads(self, files: dict[str, UploadedFile]) -> None:  # noqa: PLR0911
        try:
            file = files["post_data"]
        except (MultiValueDictKeyError, KeyError) as e:
            msg = (
                "Data Donation Processing Exception: Did not receive "
                f"expected data file from client. {e}"
            )
            log_server_exception(self.object, msg)
            return

        if not zipfile.is_zipfile(file):
            msg = (
                "Data Donation Processing Exception: Data file received "
                "from client is not a zip file."
            )
            log_server_exception(self.object, msg)
            return

        # Check if zip file contains expected file.
        unzipped_file = zipfile.ZipFile(file, "r")

        if not has_valid_zip_paths(unzipped_file):
            msg = (
                "Data Donation Processing Exception: "
                "ZIP file contains invalid file paths."
            )
            log_server_exception(self.object, msg)
            return

        if "data_donation.json" not in unzipped_file.namelist():
            msg = (
                "Data Donation Processing Exception: "
                "'data_donation.json' is not in namelist."
            )
            log_server_exception(self.object, msg)
            return

        # Process donation data.
        try:
            file_data = json.loads(
                unzipped_file.read("data_donation.json").decode("utf-8")
            )
        except UnicodeDecodeError:
            try:
                file_data = json.loads(
                    unzipped_file.read("data_donation.json").decode("latin-1")
                )
            except ValueError:
                msg = (
                    "Donated data could not be decoded - "
                    "tried utf-8 and latin-1 decoding."
                )
                log_server_exception(self.object, msg)
                return
        except JSONDecodeError:
            msg = "JSON decode error in donated data."
            log_server_exception(self.object, msg)
            return

        for upload in file_data:
            blueprint_id = upload
            blueprint_data = file_data[upload]
            try:
                blueprint = DonationBlueprint.objects.get(
                    pk=blueprint_id, project=self.object
                )
            except DonationBlueprint.DoesNotExist:
                msg = (
                    "Data Donation Processing Exception: Referenced "
                    f"blueprint with id={blueprint_id} does not exist for "
                    "this project."
                )
                log_server_exception(self.object, msg)
                return
            blueprint.process_donation(blueprint_data, self.participant)


class QuestionnaireView(ParticipationFlowBaseView):
    template_name = "ddm_participation/questionnaire.html"
    step_name = "ddm_participation:questionnaire"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Reset extra_scripts"""
        super().setup(request, *args, **kwargs)
        self.extra_scripts = []

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Skip questionnaire if no questions are defined.

        Redirects to next step if questionnaire is skipped.
        Otherwise, render questionnaire.
        """
        # Check if project is active.
        if not self.object.active:
            return redirect("ddm_participation:project_inactive", slug=self.object.slug)

        # Redirect to previous step if necessary.
        if self.steps[self.current_step] != self.step_name:
            return redirect(self.steps[self.current_step], slug=self.object.slug)

        context = self.get_context_data(object=self.object)
        if not context["q_config"]:
            self.set_step_completed()
            return redirect(self.steps[self.current_step + 1], slug=self.object.slug)
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
        return redirect(self.steps[self.current_step + 1], slug=self.object.slug)

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
        context["debriefing"] = render_user_content(
            self.object.debriefing_text, template_context
        )

        if self.object.redirect_enabled:
            context["redirect_target"] = render_user_content(
                self.object.redirect_target, template_context
            )
        else:
            context["redirect_target"] = None
        return context

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
