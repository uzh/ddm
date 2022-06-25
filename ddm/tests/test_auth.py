from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ddm.models import ResearchProfile, DonationProject
from ddm.auth import email_is_valid, user_is_owner, user_is_permitted
from ddm.tests.base import TestData


User = get_user_model()


class TestAuthenticationFlow(TestData, TestCase):

    def test_email_is_valid(self):
        valid_email = 'abc@mail.com'
        invalid_email = 'abc@liam.com'
        self.assertTrue(email_is_valid(valid_email))
        self.assertFalse(email_is_valid(invalid_email))

    def test_user_is_permitted_without_permission(self):
        self.assertFalse(user_is_permitted(self.users['no_permission']['user']))

    def test_user_is_permitted_with_ignore_email_restriction_true(self):
        self.users['no_permission']['profile'].ignore_email_restriction = True
        self.users['no_permission']['profile'].save()
        self.assertTrue(user_is_permitted(self.users['no_permission']['user']))
        self.users['no_permission']['profile'].ignore_email_restriction = False
        self.users['no_permission']['profile'].save()

    def test_user_is_owner(self):
        dp = DonationProject.objects.create(name='test-project', slug='test',
                                            owner=self.users['base']['profile'])
        self.assertTrue(user_is_owner(self.users['base']['user'], dp.pk))
        self.assertFalse(user_is_owner(self.users['no_profile']['user'], dp.pk))

    def test_login_redirect_without_profile(self):
        response = self.client.post(
            reverse('ddm-login'),
            data=self.users['no_profile']['credentials'],
            follow=True
        )
        self.assertRedirects(response, reverse('ddm-register'))

    def test_login_redirect_with_profile(self):
        response = self.client.post(
            reverse('ddm-login'),
            data=self.users['base']['credentials'],
            follow=True
        )
        self.assertRedirects(response, reverse('project-list'))

    def test_register_redirect_with_profile(self):
        self.client.login(**self.users['base']['credentials'])
        response = self.client.get(reverse('ddm-register'), follow=True)
        self.assertRedirects(response, reverse('project-list'))

    def test_register_redirect_after_registration_form_valid(self):
        self.client.login(**self.users['no_profile']['credentials'])
        response = self.client.post(
            reverse('ddm-register'),
            data={'confirmed': True, 'user': self.users['no_profile']['user'].pk},
            follow=True
        )
        self.assertRedirects(response, reverse('project-list'))

    def test_register_redirect_after_registration_form_invalid(self):
        self.client.login(**self.users['no_profile']['credentials'])
        response = self.client.post(
            reverse('ddm-register'),
            data={'confirmed': False, 'user': self.users['no_profile']['user'].pk},
            follow=True
        )
        self.assertRedirects(response, reverse('ddm-no-permission'))

    def test_register_view_creates_research_profile(self):
        self.assertFalse(ResearchProfile.objects.filter(user=self.users['no_profile']['user']).exists())
        self.client.login(**self.users['no_profile']['credentials'])
        self.client.post(
            reverse('ddm-register'),
            data={'confirmed': True, 'user': self.users['no_profile']['user'].pk},
            follow=True
        )
        self.assertTrue(ResearchProfile.objects.filter(user=self.users['no_profile']['user']).exists())

    def test_ddm_no_permission_view_200(self):
        self.client.login(**self.users['no_permission']['credentials'])
        response = self.client.get(
            reverse('ddm-no-permission'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_ddm_no_permission_view_redirect_to_login(self):
        response = self.client.get(
            reverse('ddm-no-permission'), follow=True)
        self.assertRedirects(response, reverse('ddm-login'))

    def test_ddm_no_permission_view_redirect_to_project_list(self):
        self.client.login(**self.users['base']['credentials'])
        response = self.client.get(
            reverse('ddm-no-permission'), follow=True)
        self.assertRedirects(response, reverse('project-list'))

    def test_create_user_view_redirect_authenticated_with_profile(self):
        self.client.login(**self.users['base']['credentials'])
        response = self.client.get(
            reverse('ddm-create-user'), follow=True)
        self.assertRedirects(response, reverse('project-list'))

    def test_create_user_view_redirect_authenticated_without_profile(self):
        self.client.login(**self.users['no_profile']['credentials'])
        response = self.client.get(
            reverse('ddm-create-user'), follow=True)
        self.assertRedirects(response, reverse('ddm-register'))

    def test_create_user_view_creates_user_and_profile(self):
        self.assertFalse(User.objects.filter(email='new@mail.com').exists())
        self.assertFalse(ResearchProfile.objects.filter(user__email='new@mail.com').exists())
        response = self.client.post(
            reverse('ddm-create-user'),
            data={'username': 'new_user', 'email': 'new@mail.com',
                  'password1': 'Z-6THLAqmd7H5gyUs.8dZt', 'password2': 'Z-6THLAqmd7H5gyUs.8dZt'},
            follow=True
        )
        self.assertTrue(User.objects.filter(email='new@mail.com').exists())
        self.assertTrue(ResearchProfile.objects.filter(user__email='new@mail.com').exists())
        self.assertRedirects(response, reverse('ddm-login'))

    def test_logout_view_redirect_not_logged_in(self):
        response = self.client.get(reverse('ddm-logout'), follow=True)
        self.assertRedirects(response, reverse('ddm-login'))
