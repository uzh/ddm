from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient

from ddm.models import DataDonation, QuestionnaireResponse
from ddm.tests.base import TestData


class TestDownload(TestData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.don_bp,
            participant=cls.participant_base,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data='{"data": ["donated_data", "donated_data"]}'
        )
        QuestionnaireResponse.objects.create(
            project=cls.project_base,
            participant=cls.participant_base,
            time_submitted=timezone.now(),
            data='{"data": ["response_data", "response_data"]}'
        )
        cls.project_base.collaborators.add(cls.users['base2']['profile'])
        cls.project_base.save()

    def test_download_project_data_view_exists(self):
        response = self.client.get(reverse('ddm-download-api', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 401)

    def test_download_with_regular_login_owner(self):
        self.client.login(**self.users['base']['credentials'])
        response = self.client.get(reverse('ddm-download-api', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_download_with_regular_login_collaborator(self):
        self.client.login(**self.users['base2']['credentials'])
        response = self.client.get(reverse('ddm-download-api', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_download_fails_for_user_without_permission(self):
        self.client.login(**self.users['base3']['credentials'])
        response = self.client.get(reverse('ddm-download-api', args=[self.project_base.pk]), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_download_with_valid_api_credentials(self):
        token = self.users['base']['profile'].create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get(reverse('ddm-download-api', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_download_with_invalid_api_credentials(self):
        token = 'adsjfjklsdjflkjasflk'
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = client.get(reverse('ddm-download-api', args=[self.project_base.pk]))
        self.assertEqual(response.status_code, 401)
