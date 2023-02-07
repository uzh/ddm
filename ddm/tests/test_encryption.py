from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from ddm.models.core import (
    DataDonation, DonationProject, QuestionnaireResponse, ResearchProfile,
    DonationBlueprint, Participant
)
from ddm.models.encryption import Encryption, Decryption


User = get_user_model()


class TestEncryptedFieldIsolated(TestCase):
    def test_encrypt_decrypt(self):
        text = 'test_string'
        enc = Encryption(secret='foo', salt='bar')
        enc_text = enc.encrypt(text)
        dec = Decryption(secret='foo', salt='bar')
        self.assertNotEqual(text, enc_text)
        self.assertEqual(text, dec.decrypt(enc_text))

    def test_encrypt_decrypt_explicit_public(self):
        text = 'test_string'
        dec = Decryption(secret='foo', salt='bar')
        pub = Encryption.get_public_key(secret='foo', salt='bar')
        enc_text = Encryption(public=pub).encrypt(text)
        self.assertNotEqual(text, enc_text)
        self.assertEqual(text, dec.decrypt(enc_text))


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestModelEncryption(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        base_user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        base_profile = ResearchProfile.objects.create(user=base_user)

        cls.base_project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=base_profile)

        cls.alt_project = DonationProject.objects.create(
            name='Test Project Custom',
            slug='test-project-custom',
            super_secret=True,
            secret_key='test1234',
            owner=base_profile
        )

        cls.base_blueprint = DonationBlueprint.objects.create(
            project=cls.base_project,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=None
        )
        cls.alt_blueprint = DonationBlueprint.objects.create(
            project=cls.alt_project,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=None
        )

        cls.base_participant = Participant.objects.create(
            project=cls.base_project,
            start_time=timezone.now()
        )
        cls.alt_participant = Participant.objects.create(
            project=cls.alt_project,
            start_time=timezone.now()
        )

        cls.raw_data_short = '{"some_data": "some_value"}'
        cls.raw_data_long = '{' + 100*'"some_data": "some_value",' + '}'

    def test_data_donation_encryption_default(self):
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                dd = DataDonation.objects.create(
                    project=self.base_project,
                    blueprint=self.base_blueprint,
                    participant=self.base_participant,
                    consent=True,
                    status='some status',
                    data=raw_data
                )
                self.assertNotEqual(raw_data, dd.data)
                self.assertEqual(raw_data, dd.get_decrypted_data())

    def test_questionnaire_response_encryption_default(self):
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                qr = QuestionnaireResponse.objects.create(
                    project=self.base_project,
                    participant=self.base_participant,
                    data=raw_data
                )
                self.assertNotEqual(raw_data, qr.data)
                self.assertEqual(raw_data, qr.get_decrypted_data())

    def test_data_donation_encryption_super_secret(self):
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                dd = DataDonation.objects.create(
                    project=self.alt_project,
                    blueprint=self.alt_blueprint,
                    participant=self.alt_participant,
                    consent=True,
                    status='some status',
                    data=raw_data,
                )
                self.assertNotEqual(raw_data, dd.data)
                with self.assertRaises(KeyError):
                    dd.get_decrypted_data()
                with self.assertRaises(ValueError):
                    dd.get_decrypted_data(secret='invalidSecret1234')
                self.assertEqual(raw_data, dd.get_decrypted_data(secret='test1234'))

    def test_questionnaire_response_encryption_super_secret(self):
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                qr = QuestionnaireResponse.objects.create(
                    project=self.alt_project,
                    participant=self.alt_participant,
                    data=raw_data
                )
                self.assertNotEqual(raw_data, qr.data)
                with self.assertRaises(KeyError):
                    qr.get_decrypted_data()
                with self.assertRaises(ValueError):
                    qr.get_decrypted_data(secret='invalidSecret1234')
                self.assertEqual(raw_data, qr.get_decrypted_data(secret='test1234'))
