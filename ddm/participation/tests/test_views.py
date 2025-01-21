import io
import json
import zipfile

from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, TestCase, override_settings, RequestFactory
from django.urls import reverse
from django.utils import timezone

from ddm.datadonation.models import DataDonation, DonationBlueprint, FileUploader
from ddm.logging.models import ExceptionLogEntry
from ddm.participation.models import Participant
from ddm.participation.views import (
    DataDonationView, ContinuationView, DebriefingView,
    QuestionnaireView, BriefingView
)
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import OpenQuestion


User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class ParticipationFlowBaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)

        cls.project_base = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

        cls.project_alt = DonationProject.objects.create(
            name='Alt Project', slug='alt', owner=profile)

        file_uploader = FileUploader.objects.create(
            project=cls.project_base,
            name='basic file uploader',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project_base,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=file_uploader
        )

        OpenQuestion.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint,
            name='open question',
            variable_name='open_question'
        )

        # URLs for project with questionnaire.
        slug_base = cls.project_base.slug
        cls.briefing_url = reverse(
            'ddm_participation:briefing', args=[slug_base])
        cls.dd_url = reverse(
            'ddm_participation:datadonation', args=[slug_base])
        cls.quest_url = reverse(
            'ddm_participation:questionnaire', args=[slug_base])
        cls.debriefing_url = reverse(
            'ddm_participation:debriefing', args=[slug_base])

        cls.inactive_info_page = reverse(
            'ddm_participation:project_inactive', args=[slug_base])

        # URLs for project without questionnaire.
        slug_alt = cls.project_alt.slug
        cls.briefing_url_no_quest = reverse(
            'ddm_participation:briefing', args=[slug_alt])
        cls.dd_url_no_quest = reverse(
            'ddm_participation:datadonation', args=[slug_alt])
        cls.quest_url_no_quest = reverse(
            'ddm_participation:questionnaire', args=[slug_alt])
        cls.debriefing_url_no_quest = reverse(
            'ddm_participation:debriefing', args=[slug_alt])

        # URLs for non-existing project.
        cls.briefing_url_invalid = reverse(
            'ddm_participation:briefing', args=['nope'])
        cls.dd_url_invalid = reverse(
            'ddm_participation:datadonation', args=['nope'])
        cls.quest_url_invalid = reverse(
            'ddm_participation:questionnaire', args=['nope'])
        cls.debriefing_url_invalid = reverse(
            'ddm_participation:debriefing', args=['nope'])

    def initialize_project_and_session(self):
        self.client = Client()
        self.client.get(self.briefing_url)
        self.client.get(self.briefing_url_no_quest)

    def get_participant(self, project_id):
        session = self.client.session
        participant_id = session[f'project-{project_id}']['participant_id']
        participant = Participant.objects.get(pk=int(participant_id))
        return participant

    def create_data_donation(self):
        session = self.client.session
        participant_id = session[f'project-{self.project_base.pk}']['participant_id']
        participant = Participant.objects.get(pk=int(participant_id))
        DataDonation.objects.create(
            project=self.project_base,
            blueprint=self.blueprint,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            status='success',
            data='{}'
        )


class TestBriefingView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()

    def test_project_briefing_view_registers_project(self):
        self.client.get(self.briefing_url)
        session = self.client.session
        expected_keys = ['participant_id']
        actual_keys = set(session[f'project-{self.project_base.pk}'].keys())
        assert set(expected_keys).issubset(actual_keys)

    def test_project_briefing_view_registers_participant(self):
        nr_participants_before = len(Participant.objects.all())
        self.client.get(self.briefing_url)
        self.assertGreater(len(Participant.objects.all()), nr_participants_before)

        project_session = self.client.session[f'project-{self.project_base.pk}']
        self.assertIsNotNone(project_session['participant_id'])

    def test_project_briefing_view_extracts_parameter(self):
        self.project_base.expected_url_parameters = 'testparam'
        self.project_base.url_parameter_enabled = True
        self.project_base.save()
        self.client.get(self.briefing_url + '?testparam=okay&altparam=false')
        project_session = self.client.session[f'project-{self.project_base.pk}']
        participant_id = project_session['participant_id']
        participant = Participant.objects.get(pk=participant_id)
        self.assertIn('testparam', participant.extra_data['url_param'])
        self.assertNotIn('altparam', participant.extra_data['url_param'])
        self.assertEqual(participant.extra_data['url_param']['testparam'], 'okay')

    def test_project_briefing_view_GET_valid_url(self):
        response = self.client.get(self.briefing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, BriefingView.template_name)

    def test_project_briefing_view_GET_invalid_url(self):
        response = self.client.get(self.briefing_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_project_briefing_POST(self):
        response = self.client.post(self.briefing_url)
        participant = self.get_participant(self.project_base.pk)

        self.assertEqual(participant.current_step, 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dd_url)

    def test_project_briefing_consent_yes_POST(self):
        self.project_base.briefing_consent_enabled = True
        self.project_base.save()
        self.client.get(self.briefing_url)
        response = self.client.post(
            self.briefing_url, {'briefing_consent': '1'}, follow=True)

        participant = self.get_participant(self.project_base.pk)
        self.assertEqual(participant.current_step, 1)
        self.assertRedirects(response, self.dd_url)
        self.assertEqual(participant.extra_data['briefing_consent'], '1')

    def test_project_briefing_consent_no_POST(self):
        self.project_base.briefing_consent_enabled = True
        self.project_base.save()
        self.client.get(self.briefing_url)
        response = self.client.post(self.briefing_url, {'briefing_consent': '0'})

        participant = self.get_participant(self.project_base.pk)
        self.assertEqual(participant.current_step, 3)
        self.assertRedirects(response, self.debriefing_url)
        self.assertEqual(participant.extra_data['briefing_consent'], '0')

    def test_project_briefing_consent_invalid_POST(self):
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
        request = RequestFactory().get('/sadf/<slug:slug>/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        view = DataDonationView()
        view.setup(request, **{'slug': self.project_base.slug})
        return view

    @staticmethod
    def get_zip_file(file_name, file_content):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            try:
                zip_file.writestr(file_name, file_content.encode('utf-8'))
            except UnicodeEncodeError:
                zip_file.writestr(file_name, file_content.encode('utf-8', errors='replace'))
        zip_buffer.seek(0)
        return zip_buffer

    def test_data_donation_GET_valid_url(self):
        response = self.client.get(self.dd_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, DataDonationView.template_name)

    def test_data_donation_GET_invalid_url(self):
        response = self.client.get(self.dd_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_data_donation_POST_redirect(self):
        response = self.client.post(self.dd_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.quest_url)

    def test_process_uploads_invalid_post_data(self):
        view = self.initialize_view()
        files = {}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by('date').last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn('not receive expected data file from client',
                      last_exception.message)

    def test_process_uploads_non_zip_file(self):
        view = self.initialize_view()
        files = {'post_data': 'This is not a zip file.'}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by('date').last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn('not a zip file', last_exception.message)

    def test_process_uploads_zip_file_with_missing_content(self):
        view = self.initialize_view()
        zip_buffer = self.get_zip_file('invalid_name.json', '{}')
        files = {'post_data': zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by('date').last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn('"ul_data.json" is not in namelist',
                      last_exception.message)

    def test_process_uploads_invalid_encoding(self):
        view = self.initialize_view()
        invalid_string = 'Hello, 你好, مرحبا, \ud83d'
        zip_buffer = self.get_zip_file('ul_data.json', invalid_string)
        files = {'post_data': zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by('date').last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn('decode error in donated data',
                      last_exception.message)

    def test_process_uploads_json_error(self):
        view = self.initialize_view()
        zip_buffer = self.get_zip_file('ul_data.json', '{12: "some data"}')
        files = {'post_data': zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by('date').last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn('decode error in donated data',
                      last_exception.message)

    def test_process_uploads_blueprint_does_not_exist(self):
        view = self.initialize_view()
        zip_buffer = self.get_zip_file('ul_data.json', '{"12": "some data"}')
        files = {'post_data': zip_buffer}
        exceptions_count_before = ExceptionLogEntry.objects.count()
        view.process_uploads(files)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        last_exception = ExceptionLogEntry.objects.order_by('date').last()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
        self.assertIn('blueprint with id=', last_exception.message)

    def test_process_uploads_valid_post_data(self):
        view = self.initialize_view()
        valid_data = {
            f'{self.blueprint.pk}' : {
                'consent': True,
                'extracted_data': [],
                'status': 'complete'
            }
        }
        zip_buffer = self.get_zip_file('ul_data.json', json.dumps(valid_data))
        files = {'post_data': zip_buffer}
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

    def test_questionnaire_GET_valid_url(self):
        response = self.client.get(self.quest_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, QuestionnaireView.template_name)

    def test_questionnaire_GET_invalid_url(self):
        response = self.client.get(self.quest_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_questionnaire_GET_no_questionnaire(self):
        response = self.client.get(self.quest_url_no_quest)
        self.assertRedirects(response, self.debriefing_url_no_quest)

    def test_questionnaire_POST_redirect(self):
        response = self.client.post(self.quest_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.debriefing_url)

    def test_project_inactive_redirects_to_info_page(self):
        self.project_base.active = False
        self.project_base.save()

        response = self.client.get(self.quest_url)
        self.assertRedirects(response, self.inactive_info_page)

        self.project_base.active = True
        self.project_base.save()

class TestDebriefingView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()

        participant = self.get_participant(self.project_base.pk)
        participant.current_step = 3
        participant.save()

    def test_project_debriefing_GET_valid_url(self):
        response = self.client.get(self.debriefing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, DebriefingView.template_name)

    def test_project_debriefing_GET_invalid_url(self):
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
        self.project_base.expected_url_parameters = 'testparam'
        self.project_base.redirect_target = 'http://test.test/?para={{url_parameter.testparam}}'
        self.project_base.save()

        self.client.get(self.briefing_url + '?testparam=test')

        participant = self.get_participant(self.project_base.pk)
        participant.current_step = 3
        participant.save()

        response = self.client.get(self.debriefing_url)
        self.assertEqual(
            response.context['redirect_target'],
            'http://test.test/?para=test'
        )

    def test_redirect_multiple_parameters(self):
        self.project_base.expected_url_parameters = 'testparam;testparam2'
        self.project_base.redirect_target = (
            'http://test.test/?para={{url_parameter.testparam}}&'
            'para2={{url_parameter.testparam2}}'
        )
        self.project_base.save()
        self.client.get(self.briefing_url + '?testparam=test&testparam2=test2')

        participant = self.get_participant(self.project_base.pk)
        participant.current_step = 3
        participant.save()

        response = self.client.get(self.debriefing_url)
        self.assertEqual(
            response.context['redirect_target'],
            'http://test.test/?para=test&para2=test2'
        )


class TestContinuationView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()

    def test_render_without_participant(self):
        new_client = Client()
        url = reverse(
            'ddm_participation:continuation',
            args=[self.project_base.slug]
        )
        response = new_client.get(url, data={'p': 'some-non-existing-id'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, ContinuationView.template_name)

    def test_redirect_continuation(self):
        self.client.get(self.briefing_url)
        self.client.post(self.briefing_url)
        self.client.get(self.dd_url)
        participant = self.get_participant(self.project_base.pk)
        url = reverse(
            'ddm_participation:continuation',
            args=[self.project_base.slug]
        )
        new_client = Client()
        response = new_client.get(url, data={'p': participant.external_id}, follow=True)
        self.assertRedirects(response, self.dd_url)


class TestParticipationRedirectView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()

    def test_url_without_step_redirects_to_briefing(self):
        url_input = reverse(
            'ddm_participation:redirect',
            args=[self.project_base.slug]
        )
        url_expected = reverse(
            'ddm_participation:briefing',
            args=[self.project_base.slug]
        )
        new_client = Client()
        response = new_client.get(url_input, follow=True)
        self.assertRedirects(response, url_expected)

    def test_url_without_step_redirects_to_briefing_with_query_string(self):
        query_string = '?param1=A&param2=B'
        url_input = reverse(
            'ddm_participation:redirect',
            args=[self.project_base.slug]
        ) + query_string
        url_expected = reverse(
            'ddm_participation:briefing',
            args=[self.project_base.slug]
        ) + query_string
        new_client = Client()
        response = new_client.get(url_input, follow=True)
        self.assertRedirects(response, url_expected)
