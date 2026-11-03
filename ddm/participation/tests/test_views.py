import io
import json
import zipfile

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from ddm.datadonation.models import DataDonation, DonationBlueprint, FileUploader
from ddm.datadonation.schemas import JSONParserConfig
from ddm.logging.models import ExceptionLogEntry
from ddm.participation.models import Participant
from ddm.participation.views import (
    BriefingView,
    ContinuationView,
    DataDonationView,
    DebriefingView,
    QuestionnaireView,
)
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import OpenQuestion, QuestionnaireResponse

User = get_user_model()


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class ParticipationFlowBaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)

        cls.project_base = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )

        cls.project_alt = DonationProject.objects.create(
            name="Alt Project", slug="alt", owner=profile
        )

        file_uploader = FileUploader.objects.create(
            project=cls.project_base,
            name="basic_file_uploader",
            display_name="basic file uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project_base,
            name="donation_blueprint",
            display_name="donation blueprint",
            expected_fields='"a", "b"',
            file_uploader=file_uploader,
            parser_config=JSONParserConfig().model_dump(),
        )

        OpenQuestion.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint,
            name="open question",
            variable_name="open_question",
        )

        # URLs for project with questionnaire.
        slug_base = cls.project_base.slug
        cls.briefing_url = reverse("ddm_participation:briefing", args=[slug_base])
        cls.dd_url = reverse("ddm_participation:datadonation", args=[slug_base])
        cls.quest_url = reverse("ddm_participation:questionnaire", args=[slug_base])
        cls.progress_url = reverse(
            "ddm_participation:questionnaire_progress", args=[slug_base]
        )
        cls.debriefing_url = reverse("ddm_participation:debriefing", args=[slug_base])

        cls.inactive_info_page = reverse(
            "ddm_participation:project_inactive", args=[slug_base]
        )

        # URLs for project without questionnaire.
        slug_alt = cls.project_alt.slug
        cls.briefing_url_no_quest = reverse(
            "ddm_participation:briefing", args=[slug_alt]
        )
        cls.dd_url_no_quest = reverse("ddm_participation:datadonation", args=[slug_alt])
        cls.quest_url_no_quest = reverse(
            "ddm_participation:questionnaire", args=[slug_alt]
        )
        cls.debriefing_url_no_quest = reverse(
            "ddm_participation:debriefing", args=[slug_alt]
        )

        # URLs for non-existing project.
        cls.briefing_url_invalid = reverse("ddm_participation:briefing", args=["nope"])
        cls.dd_url_invalid = reverse("ddm_participation:datadonation", args=["nope"])
        cls.quest_url_invalid = reverse(
            "ddm_participation:questionnaire", args=["nope"]
        )
        cls.debriefing_url_invalid = reverse(
            "ddm_participation:debriefing", args=["nope"]
        )

    def initialize_project_and_session(self):
        self.client = Client()
        self.client.get(self.briefing_url)
        self.client.get(self.briefing_url_no_quest)

    def get_participant(self, project_id):
        session = self.client.session
        participant_id = session[f"project-{project_id}"]["participant_id"]
        return Participant.objects.get(pk=int(participant_id))

    def create_data_donation(self):
        session = self.client.session
        participant_id = session[f"project-{self.project_base.pk}"]["participant_id"]
        participant = Participant.objects.get(pk=int(participant_id))
        DataDonation.objects.create(
            project=self.project_base,
            blueprint=self.blueprint,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            data="{}",
        )


class TestBriefingView(ParticipationFlowBaseTestCase):
    def setUp(self):
        super().setUp()

    def test_project_briefing_view_registers_project(self):
        self.client.get(self.briefing_url)
        session = self.client.session
        expected_keys = ["participant_id"]
        actual_keys = set(session[f"project-{self.project_base.pk}"].keys())
        assert set(expected_keys).issubset(actual_keys)

    def test_project_briefing_view_registers_participant(self):
        nr_participants_before = len(Participant.objects.all())
        self.client.get(self.briefing_url)
        self.assertGreater(len(Participant.objects.all()), nr_participants_before)

        project_session = self.client.session[f"project-{self.project_base.pk}"]
        self.assertIsNotNone(project_session["participant_id"])

    def test_project_briefing_view_extracts_parameter(self):
        self.project_base.expected_url_parameters = "testparam"
        self.project_base.url_parameter_enabled = True
        self.project_base.save()
        self.client.get(self.briefing_url + "?testparam=okay&altparam=false")
        project_session = self.client.session[f"project-{self.project_base.pk}"]
        participant_id = project_session["participant_id"]
        participant = Participant.objects.get(pk=participant_id)
        self.assertIn("testparam", participant.url_parameter)
        self.assertNotIn("altparam", participant.url_parameter)
        self.assertEqual(participant.url_parameter["testparam"], "okay")

    def test_project_briefing_view_get_valid_url(self):
        response = self.client.get(self.briefing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, BriefingView.template_name)

    def test_theme_link_absent_with_default_colors(self):
        response = self.client.get(self.briefing_url)
        self.assertNotIn("theme.css", response.content.decode())

    def test_theme_link_present_with_custom_colors_and_busts_cache_on_change(self):
        self.project_base.primary_color = "#aa3377"
        self.project_base.background_color = "#fdf3e7"
        self.project_base.save()

        response = self.client.get(self.briefing_url)
        content = response.content.decode()
        theme_url = reverse(
            "ddm_participation:theme_css", args=[self.project_base.slug]
        )
        self.assertIn(f"{theme_url}?v=aa3377fdf3e7", content)

        # Changing a color must change the linked URL, so a cached response
        # at the old URL is never served for the new color.
        self.project_base.primary_color = "#112233"
        self.project_base.save()
        response = self.client.get(self.briefing_url)
        content = response.content.decode()
        self.assertIn(f"{theme_url}?v=112233fdf3e7", content)
        self.assertNotIn(f"{theme_url}?v=aa3377fdf3e7", content)

    def test_project_briefing_view_get_invalid_url(self):
        response = self.client.get(self.briefing_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_project_briefing_post(self):
        response = self.client.post(self.briefing_url)
        participant = self.get_participant(self.project_base.pk)

        self.assertEqual(participant.current_step, 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dd_url)

    def test_project_briefing_consent_yes_post(self):
        self.project_base.briefing_consent_enabled = True
        self.project_base.save()
        self.client.get(self.briefing_url)
        response = self.client.post(
            self.briefing_url, {"briefing_consent": "1"}, follow=True
        )

        participant = self.get_participant(self.project_base.pk)
        self.assertEqual(participant.current_step, 1)
        self.assertRedirects(response, self.dd_url)
        self.assertEqual(participant.extra_data["briefing_consent"], "1")

    def test_project_briefing_consent_no_post(self):
        self.project_base.briefing_consent_enabled = True
        self.project_base.save()
        self.client.get(self.briefing_url)
        response = self.client.post(self.briefing_url, {"briefing_consent": "0"})

        participant = self.get_participant(self.project_base.pk)
        self.assertEqual(participant.current_step, 3)
        self.assertRedirects(response, self.debriefing_url)
        self.assertEqual(participant.extra_data["briefing_consent"], "0")

    def test_project_briefing_consent_invalid_post(self):
        self.project_base.briefing_consent_enabled = True
        self.project_base.save()
        self.client.get(self.briefing_url)
        response = self.client.post(self.briefing_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, BriefingView.template_name)

    def test_project_inactive_redirects_to_info_page(self):
        self.project_base.active = False
        self.project_base.save()

        response = self.client.get(self.briefing_url, follow=True)
        self.assertRedirects(response, self.inactive_info_page)

        self.project_base.active = True
        self.project_base.save()


class TestDonationView(ParticipationFlowBaseTestCase):
    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        self.create_data_donation()
        participant = self.get_participant(self.project_base.pk)
        participant.current_step = 1
        participant.save()

    def initialize_view(self):
        request = RequestFactory().get("/sadf/<slug:slug>/")
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        view = DataDonationView()
        view.setup(request, slug=self.project_base.slug)
        return view

    @staticmethod
    def get_zip_file(file_name, file_content):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            try:
                zip_file.writestr(file_name, file_content.encode("utf-8"))
            except UnicodeEncodeError:
                zip_file.writestr(
                    file_name, file_content.encode("utf-8", errors="replace")
                )
        zip_buffer.seek(0)
        return zip_buffer

    def test_data_donation_get_valid_url(self):
        response = self.client.get(self.dd_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, DataDonationView.template_name)

    def test_data_donation_get_invalid_url(self):
        response = self.client.get(self.dd_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_data_donation_post_redirect(self):
        zip_buffer = self.get_zip_file("data_donation.json", "{}")
        files = {"post_data": zip_buffer}
        response = self.client.post(self.dd_url, data=files)
        self.assertEqual(response.status_code, 302)

    def test_process_uploads_invalid_post_data(self):
        view = self.initialize_view()
        files = {}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn(
            "not receive expected data file from client", last_exception.message
        )

    def test_process_uploads_non_zip_file(self):
        view = self.initialize_view()
        files = {"post_data": "This is not a zip file."}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn("not a zip file", last_exception.message)

    def test_process_uploads_zip_file_with_missing_content(self):
        view = self.initialize_view()
        zip_buffer = self.get_zip_file("invalid_name.json", "{}")
        files = {"post_data": zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn(
            "does not contain expected 'data_donation.json'", last_exception.message
        )

    def test_process_uploads_invalid_encoding(self):
        view = self.initialize_view()
        invalid_string = "Hello, 你好, مرحبا, \ud83d"
        zip_buffer = self.get_zip_file("data_donation.json", invalid_string)
        files = {"post_data": zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn("decode error in donated data", last_exception.message)

    def test_process_uploads_json_error(self):
        view = self.initialize_view()
        zip_buffer = self.get_zip_file("data_donation.json", '{12: "some data"}')
        files = {"post_data": zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn("decode error in donated data", last_exception.message)

    def test_process_uploads_blueprint_does_not_exist(self):
        view = self.initialize_view()
        zip_buffer = self.get_zip_file("data_donation.json", '{"12": "some data"}')
        files = {"post_data": zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn("blueprint with id=", last_exception.message)

    def test_process_uploads_non_numeric_blueprint_id_does_not_crash(self):
        view = self.initialize_view()
        zip_buffer = self.get_zip_file("data_donation.json", '{"abc": "some data"}')
        files = {"post_data": zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn("blueprint with id=", last_exception.message)

    def test_process_uploads_continues_after_unresolvable_blueprint(self):
        other_blueprint = DonationBlueprint.objects.create(
            project=self.project_base,
            name="other_donation_blueprint",
            display_name="other donation blueprint",
            expected_fields='"a", "b"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )
        view = self.initialize_view()
        file_data = {
            "999999": "unresolvable",
            f"{other_blueprint.pk}": {
                "consent": True,
                "extractedData": [],
                "status": "DATA_EXTRACTED",
            },
        }
        zip_buffer = self.get_zip_file("data_donation.json", json.dumps(file_data))
        files = {"post_data": zip_buffer}
        donation_count_before = DataDonation.objects.count()

        view.process_uploads(files)

        self.assertEqual(DataDonation.objects.count(), donation_count_before + 1)
        self.assertTrue(
            DataDonation.objects.filter(
                blueprint=other_blueprint, participant=view.participant
            ).exists()
        )

    @override_settings(DDM_SETTINGS={"MAX_DONATION_UPLOAD_SIZE": 10})
    def test_process_uploads_oversized_data_donation_json_is_rejected(self):
        view = self.initialize_view()
        valid_data = {
            f"{self.blueprint.pk}": {
                "consent": True,
                "extractedData": [],
                "status": "DATA_EXTRACTED",
            }
        }
        zip_buffer = self.get_zip_file("data_donation.json", json.dumps(valid_data))
        files = {"post_data": zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        donation_count_before = DataDonation.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        donation_count_after = DataDonation.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertEqual(donation_count_before, donation_count_after)
        self.assertIn("exceeds the maximum allowed size", last_exception.message)

    def test_process_uploads_valid_post_data(self):
        view = self.initialize_view()
        valid_data = {
            f"{self.blueprint.pk}": {
                "consent": True,
                "extractedData": [],
                "status": "DATA_EXTRACTED",
            }
        }
        zip_buffer = self.get_zip_file("data_donation.json", json.dumps(valid_data))
        files = {"post_data": zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        donation_count_before = DataDonation.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        donation_count_after = DataDonation.objects.count()
        self.assertEqual(exceptions_count_before, exceptions_count_after)
        self.assertEqual(donation_count_before + 1, donation_count_after)

    def test_project_inactive_redirects_to_info_page(self):
        self.project_base.active = False
        self.project_base.save()

        response = self.client.get(self.dd_url)
        self.assertRedirects(response, self.inactive_info_page)

        self.project_base.active = True
        self.project_base.save()


class TestQuestionnaireView(ParticipationFlowBaseTestCase):
    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        self.create_data_donation()

        participant_base = self.get_participant(self.project_base.pk)
        participant_base.current_step = 2
        participant_base.save()

        participant_alt = self.get_participant(self.project_alt.pk)
        participant_alt.current_step = 2
        participant_alt.save()

    def test_questionnaire_get_valid_url(self):
        response = self.client.get(self.quest_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, QuestionnaireView.template_name)

    def test_questionnaire_exposes_participant_id_for_cache_scoping(self):
        participant = self.get_participant(self.project_base.pk)

        response = self.client.get(self.quest_url)

        self.assertContains(
            response, f'data-participant-id="{participant.external_id}"'
        )

    def test_questionnaire_get_invalid_url(self):
        response = self.client.get(self.quest_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_questionnaire_get_no_questionnaire(self):
        response = self.client.get(self.quest_url_no_quest)
        self.assertRedirects(response, self.debriefing_url_no_quest)

    def test_questionnaire_post_redirect(self):
        response = self.client.post(self.quest_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.debriefing_url)

    def test_questionnaire_post_missing_responses_key_does_not_crash(self):
        post_data = {"post_data": json.dumps({"questionnaire_config": []})}
        response = self.client.post(self.quest_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.debriefing_url)

        participant = self.get_participant(self.project_base.pk)
        saved = QuestionnaireResponse.objects.get(
            project=self.project_base, participant=participant
        )
        self.assertTrue(saved.is_complete)
        self.assertEqual(
            saved.get_decrypted_data(
                secret=self.project_base.secret_key,
                salt=self.project_base.get_salt(),
            ),
            {},
        )

    def test_questionnaire_post_invalid_json_does_not_crash(self):
        post_data = {"post_data": "not valid json"}

        exceptions_count_before = ExceptionLogEntry.objects.count()
        response = self.client.post(self.quest_url, data=post_data)
        exceptions_count_after = ExceptionLogEntry.objects.count()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.debriefing_url)
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        last_exception = ExceptionLogEntry.objects.order_by("date").last()
        self.assertIn("was not valid JSON", last_exception.message)

        participant = self.get_participant(self.project_base.pk)
        self.assertFalse(
            QuestionnaireResponse.objects.filter(
                project=self.project_base, participant=participant
            ).exists()
        )

    def test_project_inactive_redirects_to_info_page(self):
        self.project_base.active = False
        self.project_base.save()

        response = self.client.get(self.quest_url)
        self.assertRedirects(response, self.inactive_info_page)

        self.project_base.active = True
        self.project_base.save()


class TestQuestionnaireProgressView(ParticipationFlowBaseTestCase):
    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()

        participant_base = self.get_participant(self.project_base.pk)
        participant_base.current_step = 2
        participant_base.save()

    def post_data(self, response_value=1):
        return {
            "post_data": json.dumps(
                {
                    "responses": {"question-1": response_value},
                    "questionnaire_config": [],
                }
            )
        }

    def test_valid_session_saves_partial_response(self):
        response = self.client.post(self.progress_url, data=self.post_data())
        self.assertEqual(response.status_code, 200)

        participant = self.get_participant(self.project_base.pk)
        saved = QuestionnaireResponse.objects.get(
            project=self.project_base, participant=participant
        )
        self.assertFalse(saved.is_complete)

    def test_no_session_returns_400(self):
        new_client = Client()
        response = new_client.post(self.progress_url, data=self.post_data())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuestionnaireResponse.objects.count(), 0)

    def test_invalid_project_slug_returns_404(self):
        url = reverse("ddm_participation:questionnaire_progress", args=["nope"])
        response = self.client.post(url, data=self.post_data())
        self.assertEqual(response.status_code, 404)

    def test_missing_post_data_returns_400(self):
        response = self.client.post(self.progress_url, data={})
        self.assertEqual(response.status_code, 400)

    def test_missing_responses_key_does_not_crash(self):
        post_data = {"post_data": json.dumps({"questionnaire_config": []})}
        response = self.client.post(self.progress_url, data=post_data)
        self.assertEqual(response.status_code, 200)

        participant = self.get_participant(self.project_base.pk)
        saved = QuestionnaireResponse.objects.get(
            project=self.project_base, participant=participant
        )
        self.assertFalse(saved.is_complete)

    def test_does_not_advance_current_step(self):
        participant_before = self.get_participant(self.project_base.pk)
        step_before = participant_before.current_step

        self.client.post(self.progress_url, data=self.post_data())

        participant_after = self.get_participant(self.project_base.pk)
        self.assertEqual(participant_after.current_step, step_before)

    def test_subsequent_final_submission_updates_same_row(self):
        self.client.post(self.progress_url, data=self.post_data(response_value=1))
        participant = self.get_participant(self.project_base.pk)
        partial = QuestionnaireResponse.objects.get(
            project=self.project_base, participant=participant
        )

        self.client.post(self.quest_url, data=self.post_data(response_value=2))

        self.assertEqual(
            QuestionnaireResponse.objects.filter(
                project=self.project_base, participant=participant
            ).count(),
            1,
        )
        final = QuestionnaireResponse.objects.get(
            project=self.project_base, participant=participant
        )
        self.assertEqual(final.pk, partial.pk)
        self.assertTrue(final.is_complete)


class TestDebriefingView(ParticipationFlowBaseTestCase):
    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()

        participant = self.get_participant(self.project_base.pk)
        participant.current_step = 3
        participant.save()

    def test_project_debriefing_get_valid_url(self):
        response = self.client.get(self.debriefing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, DebriefingView.template_name)

    def test_project_debriefing_get_invalid_url(self):
        response = self.client.get(self.debriefing_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_project_inactive_redirects_to_info_page(self):
        self.project_base.active = False
        self.project_base.save()

        response = self.client.get(self.debriefing_url)
        self.assertRedirects(response, self.inactive_info_page)

        self.project_base.active = True
        self.project_base.save()


class TestRedirect(ParticipationFlowBaseTestCase):
    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        self.project_base.redirect_enabled = True
        self.project_base.url_parameter_enabled = True
        self.project_base.save()

    def test_redirect_single_parameter(self):
        self.project_base.expected_url_parameters = "testparam"
        self.project_base.redirect_target = (
            "http://test.test/?para={{url_parameter.testparam}}"
        )
        self.project_base.save()

        self.client.get(self.briefing_url + "?testparam=test")

        participant = self.get_participant(self.project_base.pk)
        participant.current_step = 3
        participant.save()

        response = self.client.get(self.debriefing_url)
        self.assertEqual(
            response.context["redirect_target"], "http://test.test/?para=test"
        )

    def test_redirect_multiple_parameters(self):
        self.project_base.expected_url_parameters = "testparam;testparam2"
        self.project_base.redirect_target = (
            "http://test.test/?para={{url_parameter.testparam}}&"
            "para2={{url_parameter.testparam2}}"
        )
        self.project_base.save()
        self.client.get(self.briefing_url + "?testparam=test&testparam2=test2")

        participant = self.get_participant(self.project_base.pk)
        participant.current_step = 3
        participant.save()

        response = self.client.get(self.debriefing_url)
        self.assertEqual(
            response.context["redirect_target"],
            "http://test.test/?para=test&para2=test2",
        )


class TestContinuationView(ParticipationFlowBaseTestCase):
    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()

    def test_render_without_participant(self):
        new_client = Client()
        url = reverse("ddm_participation:continuation", args=[self.project_base.slug])
        response = new_client.get(url, data={"p": "some-non-existing-id"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ContinuationView.template_name)

    def test_redirect_continuation(self):
        self.client.get(self.briefing_url)
        self.client.post(self.briefing_url)
        self.client.get(self.dd_url)
        participant = self.get_participant(self.project_base.pk)
        url = reverse("ddm_participation:continuation", args=[self.project_base.slug])
        new_client = Client()
        response = new_client.get(url, data={"p": participant.external_id}, follow=True)
        self.assertRedirects(response, self.dd_url)


class TestParticipationRedirectView(ParticipationFlowBaseTestCase):
    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()

    def test_url_without_step_redirects_to_briefing(self):
        url_input = reverse("ddm_participation:redirect", args=[self.project_base.slug])
        url_expected = reverse(
            "ddm_participation:briefing", args=[self.project_base.slug]
        )
        new_client = Client()
        response = new_client.get(url_input, follow=True)
        self.assertRedirects(response, url_expected)

    def test_url_without_step_redirects_to_briefing_with_query_string(self):
        query_string = "?param1=A&param2=B"
        url_input = (
            reverse("ddm_participation:redirect", args=[self.project_base.slug])
            + query_string
        )
        url_expected = (
            reverse("ddm_participation:briefing", args=[self.project_base.slug])
            + query_string
        )
        new_client = Client()
        response = new_client.get(url_input, follow=True)
        self.assertRedirects(response, url_expected)


class TestProjectThemeView(ParticipationFlowBaseTestCase):
    def test_default_colors_render_empty_stylesheet(self):
        url = reverse("ddm_participation:theme_css", args=[self.project_base.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/css")
        self.assertNotIn("--bg-color-light", response.content.decode())

    def test_custom_colors_render_overrides(self):
        self.project_base.primary_color = "#aa3377"
        self.project_base.background_color = "#fdf3e7"
        self.project_base.save()

        url = reverse("ddm_participation:theme_css", args=[self.project_base.slug])
        response = self.client.get(url)
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("--bg-color-light: #fdf3e7", content)
        self.assertIn("--color-main-green-darker: #aa3377", content)
        self.assertIn("--ddm-primary-accent: #aa3377", content)
        self.assertIn("--ddm-main-bg-color: #fdf3e7", content)

    def test_response_is_cacheable(self):
        url = reverse("ddm_participation:theme_css", args=[self.project_base.slug])
        response = self.client.get(url)
        self.assertIn("max-age", response["Cache-Control"])

    def test_alpha_channel_passed_through_to_css(self):
        self.project_base.primary_color = "#aa337780"
        self.project_base.background_color = "#fdf3e740"
        self.project_base.save()

        url = reverse("ddm_participation:theme_css", args=[self.project_base.slug])
        response = self.client.get(url)
        content = response.content.decode()

        self.assertIn("--bg-color-light: #fdf3e740", content)
        self.assertIn("--color-main-green-darker: #aa337780", content)
        self.assertIn("--ddm-primary-accent: #aa337780", content)


class TestTestMode(ParticipationFlowBaseTestCase):
    def test_valid_token_creates_fresh_flagged_participant(self):
        token = self.project_base.test_token
        n_before = Participant.objects.count()

        response = self.client.get(self.briefing_url + f"?test={token}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Participant.objects.count(), n_before + 1)

        participant = self.get_participant(self.project_base.pk)
        self.assertTrue(participant.is_test)
        self.assertFalse(participant.test_flow_broken)

    def test_revisiting_bare_test_link_starts_a_new_participant_each_time(self):
        token = self.project_base.test_token

        self.client.get(self.briefing_url + f"?test={token}")
        first = self.get_participant(self.project_base.pk)

        self.client.get(self.briefing_url + f"?test={token}")
        second = self.get_participant(self.project_base.pk)

        self.assertNotEqual(first.pk, second.pk)
        self.assertTrue(second.is_test)

    def test_step_and_page_requests_reuse_the_active_test_participant(self):
        # Using step=/page= to move to different parts of one ongoing test
        # run should not spawn a new participant each time - only a *bare*
        # test link (no step/page) is a deliberate "start over".
        token = self.project_base.test_token

        self.client.get(self.briefing_url + f"?test={token}&step=questionnaire")
        first = self.get_participant(self.project_base.pk)

        self.client.get(self.briefing_url + f"?test={token}&step=questionnaire&page=4")
        second = self.get_participant(self.project_base.pk)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(second.extra_data["test_initial_page"], "4")

        self.client.get(self.briefing_url + f"?test={token}&step=questionnaire&page=2")
        third = self.get_participant(self.project_base.pk)
        self.assertEqual(first.pk, third.pk)
        self.assertEqual(third.extra_data["test_initial_page"], "2")

    def test_banner_includes_step_and_page_navigation(self):
        token = self.project_base.test_token
        response = self.client.get(self.briefing_url + f"?test={token}")

        self.assertContains(response, 'id="test-nav-step"')
        self.assertContains(response, 'value="questionnaire"')
        self.assertContains(response, 'id="test-nav-page"')
        # The fixture's single question defaults to page 1.
        self.assertContains(response, '<option value="1">')

    def test_test_mode_helper_script_loads_on_questionnaire_page(self):
        token = self.project_base.test_token
        self.client.get(self.briefing_url + f"?test={token}&step=questionnaire")

        self.create_data_donation()
        response = self.client.get(self.quest_url)
        self.assertContains(response, "test-mode-helper.js")

    def test_bare_test_link_after_step_jump_still_starts_a_new_participant(self):
        token = self.project_base.test_token

        self.client.get(self.briefing_url + f"?test={token}&step=questionnaire")
        jumped = self.get_participant(self.project_base.pk)

        self.client.get(self.briefing_url + f"?test={token}")
        restarted = self.get_participant(self.project_base.pk)

        self.assertNotEqual(jumped.pk, restarted.pk)
        self.assertFalse(restarted.test_flow_broken)

    def test_mismatched_token_shows_disabled_page_without_creating_participant(self):
        n_before = Participant.objects.count()

        response = self.client.get(self.briefing_url + "?test=not-the-real-token")

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "ddm_participation/test_link_disabled.html")
        self.assertEqual(Participant.objects.count(), n_before)
        self.assertNotIn(f"project-{self.project_base.pk}", self.client.session)

    def test_regenerated_token_disables_old_link_but_keeps_old_participants(self):
        old_token = self.project_base.test_token
        self.client.get(self.briefing_url + f"?test={old_token}")
        old_test_participant = self.get_participant(self.project_base.pk)

        self.project_base.regenerate_test_token()

        response = self.client.get(self.briefing_url + f"?test={old_token}")
        self.assertEqual(response.status_code, 403)

        old_test_participant.refresh_from_db()
        self.assertTrue(Participant.objects.filter(pk=old_test_participant.pk).exists())

    def test_step_jump_sets_current_step_and_flags_flow_broken(self):
        # Note: Checked without `follow`: the open question in the fixture is
        # tied to a blueprint, so a jumped participant with no donation
        # would have its (now-empty) questionnaire auto-skipped to
        # debriefing by QuestionnaireView's own, unrelated logic, which
        # would otherwise be mistaken for the jump itself misbehaving.
        token = self.project_base.test_token
        response = self.client.get(
            self.briefing_url + f"?test={token}&step=questionnaire"
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.quest_url)

        participant = self.get_participant(self.project_base.pk)
        self.assertEqual(participant.current_step, 2)
        self.assertTrue(participant.test_flow_broken)
        self.assertTrue(participant.is_test)

    def test_step_jump_to_briefing_itself_does_not_flag_flow_broken(self):
        token = self.project_base.test_token
        self.client.get(self.briefing_url + f"?test={token}&step=briefing")

        participant = self.get_participant(self.project_base.pk)
        self.assertEqual(participant.current_step, 0)
        self.assertFalse(participant.test_flow_broken)

    def test_plain_test_link_without_step_does_not_flag_flow_broken(self):
        token = self.project_base.test_token
        self.client.get(self.briefing_url + f"?test={token}")

        participant = self.get_participant(self.project_base.pk)
        self.assertFalse(participant.test_flow_broken)

    def test_page_param_is_stashed_on_participant_and_passed_to_questionnaire(self):
        token = self.project_base.test_token
        self.client.get(self.briefing_url + f"?test={token}&step=questionnaire&page=3")

        participant = self.get_participant(self.project_base.pk)
        self.assertEqual(participant.extra_data["test_initial_page"], "3")

        # Give the jumped participant a donation so the blueprint-linked
        # open question isn't filtered out of q_config as "nothing to ask
        # about" - otherwise QuestionnaireView.get() would auto-skip to
        # debriefing.
        self.create_data_donation()

        response = self.client.get(self.quest_url)
        self.assertContains(response, 'data-test-initial-page="3"')

    def test_briefing_post_with_lingering_test_param_does_not_restart_participant(self):
        """A POST to the same URL (e.g. the briefing form) must not be
        treated as a fresh test-link visit, even if `test=` is still on
        the URL - otherwise every form submission would wipe progress."""
        token = self.project_base.test_token
        self.client.get(self.briefing_url + f"?test={token}")
        participant_before = self.get_participant(self.project_base.pk)

        response = self.client.post(self.briefing_url + f"?test={token}")

        participant_after = self.get_participant(self.project_base.pk)
        self.assertEqual(participant_before.pk, participant_after.pk)
        self.assertEqual(participant_after.current_step, 1)
        self.assertRedirects(response, self.dd_url)

    def test_normal_participation_link_is_unaffected(self):
        response = self.client.get(self.briefing_url)
        self.assertEqual(response.status_code, 200)

        participant = self.get_participant(self.project_base.pk)
        self.assertFalse(participant.is_test)
        self.assertFalse(participant.test_flow_broken)

    def test_test_mode_banner_shown_only_for_test_participant(self):
        normal_response = self.client.get(self.briefing_url)
        self.assertNotContains(normal_response, "Test Mode")

        token = self.project_base.test_token
        test_response = self.client.get(self.briefing_url + f"?test={token}")
        self.assertContains(test_response, "Test Mode")

    def test_banner_restart_link_points_to_current_test_token(self):
        token = self.project_base.test_token
        response = self.client.get(self.briefing_url + f"?test={token}")
        self.assertContains(response, f"{self.briefing_url}?test={token}")
