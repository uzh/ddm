from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.projects.forms import ProjectCreateForm, ProjectEditForm, BriefingEditForm
from ddm.projects.models import ResearchProfile, DonationProject

User = get_user_model()


class TestProjectCreateForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_credentials = {
            'username': 'user', 'password': '123', 'email': 'base@mail.com'
        }
        user = User.objects.create_user(**user_credentials)
        cls.user_profile = ResearchProfile.objects.create(user=user)

    def test_form_raises_error_if_super_secret_without_secret(self):
        post_data = {
            'name': 'project',
            'slug': 'project',
            'super_secret': True,
            'secret': '',
            'owner': self.user_profile
        }
        form = ProjectCreateForm(post_data)
        self.assertFalse(form.is_valid())

    def test_form_raises_error_if_super_secret_not_provided_twice(self):
        post_data = {
            'name': 'project',
            'slug': 'project',
            'super_secret': True,
            'project_password': 'secret',
            'project_password_confirm': 'different secret',
            'owner': self.user_profile
        }
        form = ProjectCreateForm(post_data)
        self.assertFalse(form.is_valid())

    def test_valid_form(self):
        post_data = {
            'name': 'project',
            'slug': 'project',
            'super_secret': False,
            'project_password': '',
            'project_password_confirm': '',
            'owner': self.user_profile,
            'contact_information': 'Some info.',
            'data_protection_statement': 'Some statement.'
        }
        form = ProjectCreateForm(post_data)
        self.assertTrue(form.is_valid())
        n_projects_before = DonationProject.objects.count()
        form.save()
        n_projects_after = DonationProject.objects.count()
        self.assertEqual(n_projects_before + 1, n_projects_after)


class TestProjectEditForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_credentials = {
            'username': 'user', 'password': '123', 'email': 'base@mail.com'
        }
        user = User.objects.create_user(**user_credentials)
        cls.user_profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=cls.user_profile)

    def test_form_valid(self):
        post_data = {
            'project': self.project.id,
            'name': 'project',
            'slug': 'project',
            'contact_information': 'Some info.',
            'data_protection_statement': 'Some statement.',
            'url_parameter_enabled': False,
            'expected_url_parameters': '',
            'redirect_enabled': False,
            'redirect_target': '',
        }
        form = ProjectEditForm(post_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_if_url_parameter_misspecified(self):
        post_data = {
            'project': self.project.id,
            'name': 'project',
            'slug': 'project',
            'contact_information': 'Some info.',
            'data_protection_statement': 'Some statement.',
            'url_parameter_enabled': True,
            'expected_url_parameters': '',
            'redirect_enabled': False,
            'redirect_target': '',
        }
        form = ProjectEditForm(post_data)
        self.assertFalse(form.is_valid())

    def test_form_invalid_if_redirect_misspecified(self):
        post_data = {
            'project': self.project.id,
            'name': 'project',
            'slug': 'project',
            'contact_information': 'Some info.',
            'data_protection_statement': 'Some statement.',
            'url_parameter_enabled': False,
            'expected_url_parameters': '',
            'redirect_enabled': True,
            'redirect_target': '',
        }
        form = ProjectEditForm(post_data)
        self.assertFalse(form.is_valid())


class TestBriefingEditForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_credentials = {
            'username': 'user', 'password': '123', 'email': 'base@mail.com'
        }
        user = User.objects.create_user(**user_credentials)
        cls.user_profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=cls.user_profile)

    def test_form_valid(self):
        post_data = {
            'briefing_text': 'Some text.',
            'briefing_consent_enabled': False,
            'briefing_consent_label_yes': '',
            'briefing_consent_label_no': None
        }
        form = BriefingEditForm(post_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_if_consent_labels_not_provided(self):
        post_data = {
            'briefing_text': 'Some text.',
            'briefing_consent_enabled': True,
            'briefing_consent_label_yes': '',
            'briefing_consent_label_no': None
        }
        form = BriefingEditForm(post_data)
        self.assertFalse(form.is_valid())
        self.assertIn('briefing_consent_label_yes', form.errors.keys())
        self.assertIn('briefing_consent_label_no', form.errors.keys())
