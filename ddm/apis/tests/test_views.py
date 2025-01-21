from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, Client
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime

from rest_framework.test import APIClient

from ddm.apis.serializers import (
    ParticipantSerializer, ResponseSerializer, ResponseSerializerWithSnapshot,
    ProjectSerializer
)
from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import OpenQuestion, QuestionnaireResponse


User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestAPIs(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.base_creds = {
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        }
        base_user = User.objects.create_user(**cls.base_creds)
        base_profile = ResearchProfile.objects.create(
            user=base_user
        )

        cls.no_perm_creds = {
            'username': 'non-perm', 'password': '123', 'email': 'non-perm@mail.com'
        }
        no_perm_user = User.objects.create_user(**cls.no_perm_creds)
        no_perm_profile = ResearchProfile.objects.create(
            user=no_perm_user
        )

        cls.project_base = DonationProject.objects.create(
            name='Base Project',
            slug='base',
            owner=base_profile
        )
        cls.project_alt = DonationProject.objects.create(
            name='Alt Project',
            slug='alternative',
            owner=no_perm_profile
        )
        cls.project_super_secret = DonationProject.objects.create(
            name='Secret Project',
            slug='super-secret',
            owner=base_profile,
            super_secret=True
        )

        cls.participant_a = Participant.objects.create(
            project=cls.project_base,
            start_time=timezone.now()
        )
        cls.participant_b = Participant.objects.create(
            project=cls.project_base,
            start_time=timezone.now()
        )
        cls.participant_c = Participant.objects.create(
            project=cls.project_alt,
            start_time=timezone.now()
        )

        cls.blueprint_a = DonationBlueprint.objects.create(
            project=cls.project_base,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=None
        )
        cls.blueprint_b = DonationBlueprint.objects.create(
            project=cls.project_base,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=None
        )

        cls.donation_pA_a = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_a,
            participant=cls.participant_a,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data=['data1_pA_bpA', 'data2_pA_bpA']
        )
        cls.donation_pA_b = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_b,
            participant=cls.participant_a,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data=['data1_pA_bpB', 'data2_pA_bpB']
        )

        cls.donation_pB_a = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_a,
            participant=cls.participant_b,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data=['data1_pB_bpA', 'data2_pB_bpA']
        )
        cls.donation_pB_b = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_b,
            participant=cls.participant_b,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data=['data1_pB_bpB', 'data2_pB_bpB']
        )

        q = OpenQuestion.objects.create(
            project=cls.project_base,
            name='open question',
            page=1,
            index=1,
            variable_name='open'
        )
        cls.q_response_a = QuestionnaireResponse.objects.create(
            project=cls.project_base,
            participant=cls.participant_a,
            time_submitted=timezone.now(),
            data=f'{{"{q.pk}": {{"response": "response_data", "question": "question text", "items": []}}}}'
        )

        cls.q_response_b = QuestionnaireResponse.objects.create(
            project=cls.project_base,
            participant=cls.participant_b,
            time_submitted=timezone.now(),
            data=f'{{"{q.pk}": {{"response": "response_data2", "question": "question text", "items": []}}}}'
        )

    def test_project_detail_api_get_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        expected_response = {
            'participants': [
                ParticipantSerializer(self.participant_a).data,
                ParticipantSerializer(self.participant_b).data,],
            'blueprints': [
                self.blueprint_a.get_config(),
                self.blueprint_b.get_config()
            ],
            'project': ProjectSerializer(self.project_base).data,
            'metadata': {
                'n_blueprints': 2,
                'n_participants': 2
            }
        }
        url = reverse('ddm_apis:project_overview', args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_donations_api_get_with_valid_api_credentials_specific_participant(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        expected_response = {
            'blueprints': {
                f'{self.blueprint_a.pk}': {
                    'blueprint_name': f'{self.blueprint_b.name}',
                    'donations': [
                        {
                            'participant': f'{self.participant_a.external_id}',
                            'data': ['data1_pA_bpA', 'data2_pA_bpA'],
                            'time_submitted': f'{localtime(self.donation_pA_a.time_submitted).isoformat()}',
                            'status': f'{self.donation_pA_a.status}',
                            'consent': self.donation_pA_a.consent,
                        },
                    ],
                },
                f'{self.blueprint_b.pk}': {
                    'blueprint_name': f'{self.blueprint_b.name}',
                    'donations': [
                        {
                            'participant': f'{self.participant_a.external_id}',
                            'data': ['data1_pA_bpB', 'data2_pA_bpB'],
                            'time_submitted': f'{localtime(self.donation_pA_b.time_submitted).isoformat()}',
                            'status': f'{self.donation_pA_b.status}',
                            'consent': self.donation_pA_b.consent,
                        },
                    ],
                }
            },
            'metadata': {
                'n_blueprints': 2
            }
        }

        url = reverse(
            'ddm_apis:donations',
            args=[self.project_base.url_id]
        ) + f'?participants={self.participant_a.external_id},nonsense'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_donations_api_get_with_valid_api_credentials_specific_blueprint(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        expected_response = {
            'blueprints': {
                f'{self.blueprint_a.pk}': {
                    'blueprint_name': f'{self.blueprint_b.name}',
                    'donations': [
                        {
                            'participant': f'{self.participant_a.external_id}',
                            'data': ['data1_pA_bpA', 'data2_pA_bpA'],
                            'time_submitted': f'{localtime(self.donation_pA_a.time_submitted).isoformat()}',
                            'status': f'{self.donation_pA_a.status}',
                            'consent': self.donation_pA_a.consent,
                        },
                        {
                            'participant': f'{self.participant_b.external_id}',
                            'data': ['data1_pB_bpA', 'data2_pB_bpA'],
                            'time_submitted': f'{localtime(self.donation_pB_a.time_submitted).isoformat()}',
                            'status': f'{self.donation_pB_a.status}',
                            'consent': self.donation_pB_a.consent,
                        }
                    ],
                },
            },
            'metadata': {
                'n_blueprints': 1
            }
        }
        url = reverse(
            'ddm_apis:donations',
            args=[self.project_base.url_id]
        )
        query_string = (
            f'?blueprints={self.blueprint_a.pk},123&'
            f'participants={self.participant_a.external_id},'
            f'{self.participant_b.external_id}'
        )
        response = client.get(url + query_string)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_donations_api_get_with_valid_api_credentials_no_participants_404(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('ddm_apis:donations', args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_donations_api_get_fails_with_invalid_api_credentials(self):
        token = self.project_alt.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('ddm_apis:donations', args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_donations_api_fails_with_no_api_credentials_created(self):
        token = self.project_base.create_token()
        key = token.key
        token.delete()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        url = reverse('ddm_apis:donations', args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_donations_api_returns_404_with_non_existing_project(self):
        token = self.project_base.create_token()
        key = token.key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        url = reverse('ddm_apis:donations', args=['non-existing-id'])
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_donations_api_returns_405_for_super_secret_project(self):
        token = self.project_super_secret.create_token()
        key = token.key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        url = reverse('ddm_apis:donations', args=[self.project_super_secret.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_responses_api_get_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        expected_response = {
            'responses': [
                ResponseSerializer(self.q_response_a).data,
                ResponseSerializer(self.q_response_b).data,
            ],
            'metadata': {
                'n_responses': len(self.project_base.questionnaireresponse_set.all())
            }
        }
        url = reverse('ddm_apis:responses', args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_responses_api_get_with_valid_api_credentials_and_snapshot(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        expected_response = {
            'responses': [
                ResponseSerializerWithSnapshot(self.q_response_a).data,
                ResponseSerializerWithSnapshot(self.q_response_b).data,
            ],
            'metadata': {
                'n_responses': len(self.project_base.questionnaireresponse_set.all())
            }
        }
        url = reverse('ddm_apis:responses', args=[self.project_base.url_id])
        query_string = f'?include_snapshot=true'
        response = client.get(url + query_string)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_responses_api_get_csv_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse(
            'ddm_apis:responses',
            args=[self.project_base.url_id]
        )
        query_string = f'?csv=true'
        response = client.get(url + query_string)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_participant_deletion_with_regular_login(self):
        self.client.login(**self.base_creds)

        new_participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now())
        external_id = new_participant.external_id

        url = reverse(
            'ddm_apis:participant_delete',
            args=[self.project_base.url_id, external_id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Participant.objects.filter(
            external_id=external_id).first())

        url = reverse(
            'ddm_apis:participant_delete',
            args=[self.project_base.url_id, 'nonsense_id']
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_participant_deletion_fails_for_user_without_permission(self):
        self.client.login(**self.no_perm_creds)

        new_participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now())
        external_id = new_participant.external_id

        url = reverse(
            'ddm_apis:participant_delete',
            args=[self.project_base.url_id, external_id]
        )
        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(Participant.objects.filter(
            external_id=external_id).first())

    def test_participant_deletion_with_token(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        new_participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now())
        external_id = new_participant.external_id

        url = reverse(
            'ddm_apis:participant_delete',
            args=[self.project_base.url_id, external_id]
        )
        response = client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Participant.objects.filter(
            external_id=external_id).first())

        url = reverse(
            'ddm_apis:participant_delete',
            args=[self.project_base.url_id, 'some_bogus_id']
        )
        response = client.delete(url)

        self.assertEqual(response.status_code, 404)

    def test_participant_deletion_fails_with_invalid_token(self):
        token = self.project_alt.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        new_participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now())
        external_id = new_participant.external_id

        url = reverse(
            'ddm_apis:participant_delete',
            args=[self.project_base.url_id, external_id]
        )
        response = client.delete(url, follow=True)

        self.assertEqual(response.status_code, 401)
        self.assertIsNotNone(Participant.objects.filter(
            external_id=external_id).first())

    def test_delete_project_data_with_regular_login_owner(self):
        self.client.login(**self.base_creds)
        url = reverse(
            'ddm_apis:project_data_delete',
            args=[self.project_base.url_id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete_project_data_fails_for_user_without_permission(self):
        self.client.login(**self.no_perm_creds)
        url = reverse(
            'ddm_apis:project_data_delete',
            args=[self.project_base.url_id]
        )
        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_delete_project_data_fails_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse(
            'ddm_apis:project_data_delete',
            args=[self.project_base.url_id]
        )
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(response.data)

    def test_delete_project_data_fails_with_invalid_api_credentials(self):
        token = self.project_alt.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse(
            'ddm_apis:project_data_delete',
            args=[self.project_base.url_id]
        )
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_project_data_with_no_api_credentials_created(self):
        token = self.project_base.create_token()
        key = token.key
        token.delete()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        url = reverse(
            'ddm_apis:project_data_delete',
            args=[self.project_base.url_id]
        )
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_download_project_detail_view_valid_login(self):
        self.client.login(**self.base_creds)
        url = reverse(
            'ddm_apis:download_project_details',
            args=[self.project_base.url_id]
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_download_project_detail_view_invalid_login(self):
        self.client.login(**self.no_perm_creds)
        url = reverse(
            'ddm_apis:download_project_details',
            args=[self.project_base.url_id]
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_download_project_detail_view_not_logged_in(self):
        client = Client()
        url = reverse(
            'ddm_apis:download_project_details',
            args=[self.project_base.url_id]
        )
        response = client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)
