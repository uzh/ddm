from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from ddm.models.core import (
    DataDonation, Participant, ResearchProfile, DonationProject,
    DonationBlueprint, FileUploader
)
from ddm.models.questions import OpenQuestion


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
        cls.briefing_url = reverse('briefing', args=[slug_base])
        cls.dd_url = reverse('data-donation', args=[slug_base])
        cls.quest_url = reverse('questionnaire', args=[slug_base])
        cls.debriefing_url = reverse('debriefing', args=[slug_base])

        # URLs for project without questionnaire.
        slug_alt = cls.project_alt.slug
        cls.briefing_url_no_quest = reverse('briefing', args=[slug_alt])
        cls.dd_url_no_quest = reverse('data-donation', args=[slug_alt])
        cls.quest_url_no_quest = reverse('questionnaire', args=[slug_alt])
        cls.debriefing_url_no_quest = reverse('debriefing', args=[slug_alt])

        # URLs for non-existing project.
        cls.briefing_url_invalid = reverse('briefing', args=['nope'])
        cls.dd_url_invalid = reverse('data-donation', args=['nope'])
        cls.quest_url_invalid = reverse('questionnaire', args=['nope'])
        cls.debriefing_url_invalid = reverse('debriefing', args=['nope'])

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

    def test_project_briefing_view_GET_valid_url(self):
        response = self.client.get(self.briefing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/briefing.html')

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
        self.assertTemplateUsed(response, 'ddm/public/briefing.html')


class TestDonationView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        self.create_data_donation()
        participant = self.get_participant(self.project_base.pk)
        participant.current_step = 1
        participant.save()

    def test_data_donation_GET_valid_url(self):
        response = self.client.get(self.dd_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/data_donation.html')

    def test_data_donation_GET_invalid_url(self):
        response = self.client.get(self.dd_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_data_donation_POST_redirect(self):
        response = self.client.post(self.dd_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.quest_url)


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
        self.assertTemplateUsed(response, 'ddm/public/questionnaire.html')

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
        self.assertTemplateUsed(response, 'ddm/public/debriefing.html')

    def test_project_debriefing_GET_invalid_url(self):
        response = self.client.get(self.debriefing_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)


class TestRedirect(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        self.project_base.redirect_enabled = True
        self.project_base.url_parameter_enabled = True
        self.project_base.save()

    def test_redirect_single_parameter(self):
        self.project_base.expected_url_parameters = 'testparam'
        self.project_base.redirect_target = 'http://test.test/?para={{participant.data.url_param.testparam}}'
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
        self.project_base.redirect_target = 'http://test.test/?para={{participant.data.url_param.testparam}}&para2={{participant.data.url_param.testparam2}}'
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
