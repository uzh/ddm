from django.contrib import auth
from django.test import TestCase, override_settings, Client
from django.contrib.auth import get_user_model

from ddm.auth.utils import email_is_valid, user_has_project_access, user_is_permitted
from ddm.projects.models import ResearchProfile, DonationProject

User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestAUthUtils(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.valid_creds = {
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        }
        cls.valid_user = User.objects.create_user(**cls.valid_creds)
        cls.valid_profile = ResearchProfile.objects.create(user=cls.valid_user)

        cls.non_permission_creds = {
            'username': 'no_per', 'password': '123', 'email': 'noperm@liam.com'
        }
        cls.user_wo_permission = User.objects.create_user(**cls.non_permission_creds)
        cls.profile_wo_permission = ResearchProfile.objects.create(user=cls.user_wo_permission)

        cls.wo_profile_creds = {
            'username': 'no_prof', 'password': '123', 'email': 'noprof@mail.com'
        }
        cls.user_wo_profile = User.objects.create_user(**cls.wo_profile_creds)

        cls.superuser = User.objects.create_superuser('user', 'some@mail.com', 'password')

    def test_email_is_valid(self):
        self.assertTrue(email_is_valid('some-address@mail.com'))

    def test_email_is_invalid(self):
        self.assertFalse(email_is_valid('some-address@mail.ch'))
        self.assertFalse(email_is_valid('some-address@liam.com'))

    def test_user_has_project_access(self):
        project = DonationProject.objects.create(
            name='test-project', slug='test', owner=self.valid_profile)
        self.assertTrue(user_has_project_access(self.valid_user, project))

    def test_user_has_no_project_access(self):
        project = DonationProject.objects.create(
            name='test-project', slug='test', owner=self.valid_profile)
        self.assertFalse(user_has_project_access(self.user_wo_profile, project))
        self.assertFalse(user_has_project_access(self.user_wo_permission, project))
        anonymous_user = auth.get_user(self.client)
        self.assertFalse(user_has_project_access(anonymous_user, project))

    def test_user_is_permitted(self):
        self.assertTrue(user_is_permitted(self.valid_user))
        self.assertTrue(user_is_permitted(self.superuser))
        self.profile_wo_permission.ignore_email_restriction = True
        self.profile_wo_permission.save()
        self.assertTrue(user_is_permitted(self.user_wo_permission))
        self.assertTrue(user_is_permitted(self.user_wo_profile))

    def test_user_is_not_permitted(self):
        self.assertFalse(user_is_permitted(self.user_wo_permission))
        client = Client()
        anonymous_user = auth.get_user(client)
        self.assertFalse(user_is_permitted(anonymous_user))
