from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from ddm.projects.models import DonationProject, ResearchProfile


User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestDonationProject(TestCase):
    @classmethod
    def setUpTestData(cls):
        credentials = {
            'username': 'no_prof', 'password': '123', 'email': 'u@mail.com'
        }
        cls.user = User.objects.create_user(**credentials)
        cls.user_profile = ResearchProfile.objects.create(user=cls.user)
        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=cls.user_profile)

    def test_project_owner_cannot_be_null_on_create(self):
        invalid_project = DonationProject(name='test_project', slug='test')
        self.assertRaises(ValidationError, invalid_project.save)

    def test_get_statistics(self):
        statistics_keys = [
            'n_started',
            'n_completed',
            'completion_rate',
            'n_donations',
            'n_errors',
            'average_time'
        ]
        for key in statistics_keys:
            self.assertIn(key, self.project.get_statistics())

    def test_create_url_id(self):
        new_project = DonationProject.objects.create(
            name='test project', slug='test', owner=self.user_profile)
        self.assertIsNotNone(new_project.url_id)
        self.assertEqual(len(new_project.url_id), 8)
