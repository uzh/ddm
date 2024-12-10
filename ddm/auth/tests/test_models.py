import datetime

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import exceptions

from ddm.auth.models import ProjectTokenAuthenticator, ProjectAccessToken
from ddm.projects.models import ResearchProfile, DonationProject


User = get_user_model()


class TestCustomTokenAuthenticator(TestCase):

    @classmethod
    def setUpTestData(cls):
        # User
        base_creds = {
            'username': 'base_user', 'password': '123', 'email': 'base@mail.com'
        }
        base_user = User.objects.create_user(**base_creds)
        base_user_profile = ResearchProfile.objects.create(user=base_user)

        # Project
        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=base_user_profile
        )

        # Authenticator
        cls.authenticator = ProjectTokenAuthenticator()
        cls.token = ProjectAccessToken.objects.create(
            project=cls.project, created=timezone.now(), expiration_date=None
        )

    def test_valid_token_without_expiration(self):
        validated_token = self.authenticator.authenticate_credentials(
            self.token, self.project.url_id)[1]
        self.assertEqual(self.token, validated_token)

    def test_valid_token_with_expiration(self):
        self.token.delete()
        token = ProjectAccessToken.objects.create(
            project=self.project,
            created=timezone.now(),
            expiration_date=timezone.now() + datetime.timedelta(days=2)
        )
        validated_token = self.authenticator.authenticate_credentials(
            token, self.project.url_id)[1]
        self.assertEqual(token, validated_token)

    def test_invalid_token(self):
        token = 'rubbish'
        self.assertRaises(
            exceptions.AuthenticationFailed,
            self.authenticator.authenticate_credentials,
            token, self.project.url_id
        )

    def test_without_token(self):
        self.assertRaises(
            exceptions.AuthenticationFailed,
            self.authenticator.authenticate_credentials,
            None, self.project.url_id
        )

    def test_expired_token(self):
        self.token.delete()
        expired_token = ProjectAccessToken.objects.create(
            project=self.project,
            created=timezone.now(),
            expiration_date=datetime.datetime(2022, 2, 2, 22, 22).replace(tzinfo=datetime.timezone.utc)
        )
        self.assertRaises(
            exceptions.AuthenticationFailed,
            self.authenticator.authenticate_credentials,
            expired_token, self.project.url_id
        )
