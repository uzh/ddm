import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from ddm.models.auth import CustomTokenAuthenticator, CustomToken
from ddm.models.core import ResearchProfile, DonationProject
from ddm.auth import email_is_valid, user_is_owner, user_is_permitted
from ddm.tests.base import TestData
from rest_framework import exceptions


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

    def test_register_redirect_with_profile(self):
        self.client.login(**self.users['base']['credentials'])
        response = self.client.get(reverse('ddm-register-researcher'), follow=True)
        self.assertRedirects(response, reverse('project-list'))

    def test_register_redirect_after_registration_form_valid(self):
        self.client.login(**self.users['no_profile']['credentials'])
        response = self.client.post(
            reverse('ddm-register-researcher'),
            data={'confirmed': True, 'user': self.users['no_profile']['user'].pk},
            follow=True
        )
        self.assertRedirects(response, reverse('project-list'))

    def test_register_redirect_after_registration_form_invalid(self):
        self.client.login(**self.users['no_profile']['credentials'])
        response = self.client.post(
            reverse('ddm-register-researcher'),
            data={'confirmed': False, 'user': self.users['no_profile']['user'].pk},
            follow=True
        )
        self.assertRedirects(response, reverse('ddm-no-permission'))

    def test_register_view_creates_research_profile(self):
        self.assertFalse(ResearchProfile.objects.filter(user=self.users['no_profile']['user']).exists())
        self.client.login(**self.users['no_profile']['credentials'])
        self.client.post(
            reverse('ddm-register-researcher'),
            data={'confirmed': True, 'user': self.users['no_profile']['user'].pk},
            follow=True
        )
        self.assertTrue(ResearchProfile.objects.filter(user=self.users['no_profile']['user']).exists())

    def test_ddm_no_permission_view_200(self):
        self.client.login(**self.users['no_permission']['credentials'])
        response = self.client.get(
            reverse('ddm-no-permission'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_ddm_no_permission_view_redirect_to_project_list(self):
        self.client.login(**self.users['base']['credentials'])
        response = self.client.get(
            reverse('ddm-no-permission'), follow=True)
        self.assertRedirects(response, reverse('project-list'))


class TestAuthCustomTokenAuthenticator(TestCase):

    @classmethod
    def setUpTestData(cls):
        # User
        base_user_credentials = {'username': 'base_user', 'password': '123', 'email': 'base@mail.com'}
        base_user = User.objects.create_user(**base_user_credentials)
        base_user_profile = ResearchProfile.objects.create(user=base_user)

        # Project
        cls.project = DonationProject.objects.create(name='Base Project', slug='base', owner=base_user_profile)

        # Authenticator
        cls.authenticator = CustomTokenAuthenticator()
        cls.token = CustomToken.objects.create(
            project=cls.project,
            created=timezone.now(),
            expiration_date=None
        )

    def test_valid_token_without_expiration(self):
        validated_token = self.authenticator.authenticate_credentials(self.token)[1]
        self.assertEqual(self.token, validated_token)

    def test_valid_token_with_expiration(self):
        self.token.delete()
        token = CustomToken.objects.create(
            project=self.project,
            created=timezone.now(),
            expiration_date=timezone.now() + datetime.timedelta(days=2)
        )
        validated_token = self.authenticator.authenticate_credentials(token)[1]
        self.assertEqual(token, validated_token)

    def test_invalid_token(self):
        token = 'rubbish'
        self.assertRaises(exceptions.AuthenticationFailed, self.authenticator.authenticate_credentials, token)

    def test_without_token(self):
        self.assertRaises(exceptions.AuthenticationFailed, self.authenticator.authenticate_credentials, None)

    def test_expired_token(self):
        self.token.delete()
        expired_token = CustomToken.objects.create(
            project=self.project,
            created=timezone.now(),
            expiration_date=datetime.datetime(2022, 2, 2, 22, 22).replace(tzinfo=timezone.utc)
        )
        self.assertRaises(exceptions.AuthenticationFailed, self.authenticator.authenticate_credentials, expired_token)
