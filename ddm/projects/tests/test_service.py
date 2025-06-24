from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.projects.service import get_url_parameters, get_participant_variables, get_donation_variables, \
    get_questionnaire_variables
from ddm.questionnaire.models import QuestionnaireResponse, OpenQuestion, get_filter_config_id

User = get_user_model()

class TestDonationProject(TestCase):
    @classmethod
    def setUpTestData(cls):
        credentials = {
            'username': 'no_prof', 'password': '123', 'email': 'u@mail.com'
        }
        cls.user = User.objects.create_user(**credentials)
        cls.user_profile = ResearchProfile.objects.create(user=cls.user)
        cls.project = DonationProject.objects.create(
            name='Base Project',
            slug='base',
            owner=cls.user_profile,
            url_parameter_enabled=True,
            expected_url_parameters='param_a;param_b'
        )

        cls.participant = Participant.objects.create(
            project=cls.project,
            start_time=timezone.now(),
            extra_data={'url_param': {'param_a': 'something'}}
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name='some name',
            expected_fields=''
        )

        DataDonation.objects.create(
            project=cls.project,
            blueprint=cls.blueprint,
            participant=cls.participant,
            consent=True,
            status='success',
            data='{}'
        )

        cls.open_question = OpenQuestion.objects.create(
            project=cls.project,
            name='some name',
            variable_name='open_question_1'
        )

        cls.response = QuestionnaireResponse.objects.create(
            project=cls.project,
            participant=cls.participant,
            data=f'{{"{get_filter_config_id(cls.open_question)}": "some answer"}}'
        )

    def test_get_url_parameters(self):
        result = get_url_parameters(self.project)
        expected = {'_url_param_a': None, '_url_param_b': None}
        self.assertDictEqual(result, expected)

    def test_get_url_parameters_participant(self):
        result = get_url_parameters(self.project, self.participant)
        expected = {'_url_param_a': 'something', '_url_param_b': None}
        self.assertDictEqual(result, expected)

    def test_get_participant_variables(self):
        result = get_participant_variables()
        expected = {
            '_participant_id': None,
            '_start_time': None,
            '_end_time': None,
            '_completed': None,
            '_briefing_consent': None,
        }
        self.assertDictEqual(result, expected)

    def test_get_participant_variables_participant(self):
        result = get_participant_variables(self.participant)
        expected = {
            '_participant_id': self.participant.external_id,
            '_start_time': self.participant.start_time.replace(microsecond=0).isoformat(),
            '_end_time': None,
            '_completed': self.participant.completed,
            '_briefing_consent': self.participant.extra_data.get('briefing_consent', None),
        }
        self.assertDictEqual(result, expected)

    def test_get_donation_variables(self):
        result = get_donation_variables()
        expected = {
            '_donation_n_success': None,
            '_donation_n_pending': None,
            '_donation_n_failed': None,
            '_donation_n_consent': None,
            '_donation_n_no_consent': None,
            '_donation_n_no_data_extracted': None,
        }
        self.assertDictEqual(result, expected)

    def test_get_donation_variables_participant(self):
        result = get_donation_variables(self.participant)
        expected = {
            '_donation_n_success': 1,
            '_donation_n_pending': 0,
            '_donation_n_failed': 0,
            '_donation_n_consent': 1,
            '_donation_n_no_consent': 0,
            '_donation_n_no_data_extracted': 0,
        }
        self.assertDictEqual(result, expected)

    def test_get_questionnaire_variables(self):
        result = get_questionnaire_variables(self.project)
        expected = {
            '_quest_time_submitted': None,
            f'{self.open_question.variable_name}': None
        }
        self.assertDictEqual(result, expected)

    def test_get_questionnaire_variables_participant(self):
        result = get_questionnaire_variables(self.project, self.participant)
        expected = {
            '_quest_time_submitted': self.response.time_submitted.replace(microsecond=0).isoformat(),
            f'{self.open_question.variable_name}': 'some answer'
        }
        self.assertDictEqual(result, expected)
