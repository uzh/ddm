from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient

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
        base_profile = ResearchProfile.objects.create(user=base_user)

        cls.no_perm_creds = {
            'username': 'non-perm', 'password': '123', 'email': 'non-perm@mail.com'
        }
        no_perm_user = User.objects.create_user(**cls.no_perm_creds)
        no_perm_profile = ResearchProfile.objects.create(user=no_perm_user)

        cls.project_base = DonationProject.objects.create(
            name='Base Project', slug='base', owner=base_profile)
        cls.project_alt = DonationProject.objects.create(
            name='Alt Project', slug='alternative', owner=no_perm_profile)

        cls.participant = Participant.objects.create(
            project=cls.project_base,
            start_time=timezone.now()
        )
        cls.participant_two = Participant.objects.create(
            project=cls.project_base,
            start_time=timezone.now()
        )
        blueprint = DonationBlueprint.objects.create(
            project=cls.project_base,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=None
        )
        DataDonation.objects.create(
            project=cls.project_base,
            blueprint=blueprint,
            participant=cls.participant,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data={'data': ['donated_data', 'donated_data']}
        )
        DataDonation.objects.create(
            project=cls.project_base,
            blueprint=blueprint,
            participant=cls.participant_two,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data={'data': ['donated_data2', 'donated_data2']}
        )
        q = OpenQuestion.objects.create(
            project=cls.project_base,
            name='open question',
            page=1,
            index=1,
            variable_name='open'
        )
        cls.q_response = QuestionnaireResponse.objects.create(
            project=cls.project_base,
            participant=cls.participant,
            time_submitted=timezone.now(),
            data=f'{{"{q.pk}": {{"response": "response_data", "question": "question text", "items": []}}}}'
        )
        cls.q_response_two = QuestionnaireResponse.objects.create(
            project=cls.project_base,
            participant=cls.participant_two,
            time_submitted=timezone.now(),
            data=f'{{"{q.pk}": {{"response": "response_data2", "question": "question text", "items": []}}}}'
        )

    def test_download_project_data_view_exists(self):
        response = self.client.get(
            reverse('ddm_apis:project_data', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 401)

    def test_download_project_data_with_regular_login_owner(self):
        self.client.login(**self.base_creds)
        response = self.client.get(
            reverse('ddm_apis:project_data', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 200)

    def test_download_project_data_fails_for_user_without_permission(self):
        self.client.login(**self.no_perm_creds)
        response = self.client.get(
            reverse('ddm_apis:project_data', args=[self.project_base.pk]), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_download_project_data_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get(
            reverse('ddm_apis:project_data', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 200)

    def test_download_project_data_with_invalid_api_credentials(self):
        token = self.project_alt.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get(
            reverse('ddm_apis:project_data', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 401)

    def test_download_project_data_with_no_api_credentials_created(self):
        token = self.project_base.create_token()
        key = token.key
        token.delete()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        response = client.get(
            reverse('ddm_apis:project_data', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 401)

    def test_delete_project_data_with_regular_login_owner(self):
        self.client.login(**self.base_creds)
        response = self.client.delete(
            reverse('ddm_apis:project_data_delete', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete_project_data_fails_for_user_without_permission(self):
        self.client.login(**self.no_perm_creds)
        response = self.client.delete(
            reverse('ddm_apis:project_data_delete', args=[self.project_base.pk]), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_delete_project_data_fails_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.delete(
            reverse('ddm_apis:project_data_delete', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(response.data)

    def test_delete_project_data_fails_with_invalid_api_credentials(self):
        token = self.project_alt.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.delete(
            reverse('ddm_apis:project_data_delete', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 403)

    def test_delete_project_data_with_no_api_credentials_created(self):
        token = self.project_base.create_token()
        key = token.key
        token.delete()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + key)
        response = client.delete(
            reverse('ddm_apis:project_data_delete', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 403)
