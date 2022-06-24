from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from ddm.models import DonationProject, ResearchProfile


User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestDonationProject(TestCase):
    def setUp(self):
        credentials = {'username': 'no_prof', 'password': '123', 'email': 'u@mail.com'}
        self.user = User.objects.create_user(**credentials)
        self.user_profile = ResearchProfile.objects.create(user=self.user)

    def test_project_owner_cannot_be_null_on_create(self):
        invalid_project = DonationProject(name='test_project', slug='test')
        self.assertRaises(ValidationError, invalid_project.save)

    def test_project_owner_cannot_be_collaborator(self):
        invalid_project = DonationProject.objects.create(name='test_project', slug='test', owner=self.user_profile)
        invalid_project.collaborators.add(self.user_profile)
        self.assertRaises(ValidationError, invalid_project.save)
