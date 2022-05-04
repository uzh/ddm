from django.test import TestCase
from django.utils import timezone
from ddm.models import (
    DataDonation, DonationProject, DonationBlueprint, Encryption, Participant,
    QuestionnaireResponse
)


class TestEncryptedFieldIsolated(TestCase):
    def test_encrypt_decrypt(self):
        text = 'teststring'
        enc = Encryption(secret="foo", salt="bar")
        enc_text = enc.encrypt(text)
        self.assertNotEqual(text, enc_text)
        self.assertEqual(text, enc.decrypt(enc_text))


class TestModelEncryption(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = DonationProject.objects.create(
            name='Test Project',
            slug='test-project'
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name='donation blueprint',
            expected_fields='a,b',
            extracted_fields='a'
        )
        cls.participant = Participant.objects.create(
            project=cls.project,
            start_time=timezone.now()
        )
        cls.custom_project = DonationProject.objects.create(
            name='Test Project Custom',
            slug='test-project-custom',
            secret='test1234'
        )

    def test_data_donation_encryption_default(self):
        raw_data = '["somedata": "somevalue"]'
        dd = DataDonation.objects.create(
            project=self.project,
            blueprint=self.blueprint,
            participant=self.participant,
            consent=True,
            status='some status',
            data=raw_data
        )
        self.assertNotEqual(raw_data, dd.data)
        self.assertEqual(raw_data, dd.get_decrypted_data())

    def test_questionnaire_response_encryption_default(self):
        raw_data = '["somedata": "somevalue"]'
        qr = QuestionnaireResponse.objects.create(
            project=self.project,
            participant=self.participant,
            data=raw_data
        )
        self.assertNotEqual(raw_data, qr.data)
        self.assertEqual(raw_data, qr.get_decrypted_data())

    def test_data_donation_encryption_custom(self):
        raw_data = '["somedata": "somevalue"]'
        dd = DataDonation.objects.create(
            project=self.custom_project,
            blueprint=self.blueprint,
            participant=self.participant,
            consent=True,
            status='some status',
            data=raw_data,
        )
        self.assertNotEqual(raw_data, dd.data)
        self.assertEqual(raw_data, dd.get_decrypted_data(secret='test1234'))

    def test_questionnaire_response_encryption_custom(self):
        raw_data = '["somedata": "somevalue"]'
        qr = QuestionnaireResponse.objects.create(
            project=self.custom_project,
            participant=self.participant,
            data=raw_data
        )
        self.assertNotEqual(raw_data, qr.data)
        self.assertEqual(raw_data, qr.get_decrypted_data(secret='test1234'))
