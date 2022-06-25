from django.test import TestCase

from ddm.models import DataDonation, DonationProject, Encryption, QuestionnaireResponse
from ddm.tests.base import TestData


class TestEncryptedFieldIsolated(TestCase):
    def test_encrypt_decrypt(self):
        text = 'test_string'
        enc = Encryption(secret='foo', salt='bar')
        enc_text = enc.encrypt(text)
        self.assertNotEqual(text, enc_text)
        self.assertEqual(text, enc.decrypt(enc_text))

    def test_encrypt_decrypt_explicit_public(self):
        text = 'test_string'
        enc = Encryption(secret='foo', salt='bar')
        pub = enc.public_key
        enc_text = Encryption(public_key=pub).encrypt(text)
        self.assertNotEqual(text, enc_text)
        self.assertEqual(text, enc.decrypt(enc_text))


class TestModelEncryption(TestData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.custom_project = DonationProject.objects.create(
            name='Test Project Custom',
            slug='test-project-custom',
            super_secret=True,
            secret_key='test1234',
            owner=cls.users['base']['profile']
        )
        cls.raw_data_short = '{"some_data": "some_value"}'
        cls.raw_data_long = '{' + 100*'"some_data": "some_value",' + '}'

    def test_data_donation_encryption_default(self):
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                dd = DataDonation.objects.create(
                    project=self.project_base,
                    blueprint=self.don_bp,
                    participant=self.participant_base,
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
                    project=self.project_base,
                    participant=self.participant_base,
                    data=raw_data
                )
                self.assertNotEqual(raw_data, qr.data)
                self.assertEqual(raw_data, qr.get_decrypted_data())

    def test_data_donation_encryption_custom(self):
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                dd = DataDonation.objects.create(
                    project=self.custom_project,
                    blueprint=self.don_bp,
                    participant=self.participant_base,
                    consent=True,
                    status='some status',
                    data=raw_data,
                )
                self.assertNotEqual(raw_data, dd.data)
                self.assertEqual(raw_data, dd.get_decrypted_data())

    def test_questionnaire_response_encryption_custom(self):
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                qr = QuestionnaireResponse.objects.create(
                    project=self.custom_project,
                    participant=self.participant_base,
                    data=raw_data
                )
                self.assertNotEqual(raw_data, qr.data)
                self.assertEqual(raw_data, qr.get_decrypted_data())
