from Crypto.PublicKey import RSA
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.datadonation.schemas import JSONParserConfig
from ddm.encryption.models import (
    Decryption,
    Encryption,
    unwrap_private_key,
    wrap_private_key,
)
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import QuestionnaireResponse

User = get_user_model()


class TestEncryptedFieldIsolated(TestCase):
    def test_encrypt_decrypt(self):
        text = "test_string"
        enc = Encryption(secret="foo", salt="bar")
        enc_text = enc.encrypt(text)
        dec = Decryption(secret="foo", salt="bar")
        self.assertNotEqual(text, enc_text)
        self.assertEqual(text, dec.decrypt(enc_text))

    def test_encrypt_decrypt_explicit_public(self):
        text = "test_string"
        dec = Decryption(secret="foo", salt="bar")
        pub = Encryption.get_public_key(secret="foo", salt="bar")
        enc_text = Encryption(public=pub).encrypt(text)
        self.assertNotEqual(text, enc_text)
        self.assertEqual(text, dec.decrypt(enc_text))

    def test_wrap_unwrap_private_key_round_trip(self):
        key = RSA.generate(2048)
        private_key_der = key.export_key(format="DER")
        wrapped = wrap_private_key("some secret", private_key_der)
        self.assertNotEqual(wrapped, private_key_der)
        self.assertEqual(unwrap_private_key("some secret", wrapped), private_key_der)

    def test_unwrap_private_key_wrong_secret_raises(self):
        key = RSA.generate(2048)
        wrapped = wrap_private_key("correct secret", key.export_key(format="DER"))
        with self.assertRaises(ValueError):
            unwrap_private_key("wrong secret", wrapped)

    def test_unwrap_private_key_tampered_ciphertext_raises(self):
        key = RSA.generate(2048)
        wrapped = wrap_private_key("some secret", key.export_key(format="DER"))
        tampered = wrapped[:-1] + bytes([wrapped[-1] ^ 0xFF])
        with self.assertRaises(ValueError):
            unwrap_private_key("some secret", tampered)

    def test_decryption_private_key_bypass(self):
        key = RSA.generate(2048)
        text = "test_string"
        enc_text = Encryption(public=key.publickey().export_key()).encrypt(text)
        dec = Decryption(private_key=key.export_key(format="DER"))
        self.assertEqual(text, dec.decrypt(enc_text))


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestModelEncryption(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        base_user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        base_profile = ResearchProfile.objects.create(user=base_user)

        cls.base_project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=base_profile
        )

        cls.alt_project = DonationProject.objects.create(
            name="Test Project Custom",
            slug="test-project-custom",
            super_secret=True,
            secret_key="test1234",
            owner=base_profile,
        )

        cls.base_blueprint = DonationBlueprint.objects.create(
            project=cls.base_project,
            name="donation blueprint",
            expected_fields='"a", "b"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )
        cls.alt_blueprint = DonationBlueprint.objects.create(
            project=cls.alt_project,
            name="donation blueprint",
            expected_fields='"a", "b"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )

        cls.base_participant = Participant.objects.create(
            project=cls.base_project, start_time=timezone.now()
        )
        cls.alt_participant = Participant.objects.create(
            project=cls.alt_project, start_time=timezone.now()
        )

        cls.raw_data_short = '{"some_data": "some_value"}'
        cls.raw_data_long = "{" + 100 * '"some_data": "some_value",' + "}"

    def test_data_donation_encryption_default(self):
        # A participant has at most one DataDonation per blueprint, so each
        # iteration re-saves the same instance.
        dd = DataDonation(
            project=self.base_project,
            blueprint=self.base_blueprint,
            participant=self.base_participant,
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
        )
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                dd.data = raw_data
                dd.save()
                self.assertNotEqual(raw_data, dd.data)
                self.assertEqual(
                    raw_data,
                    dd.get_decrypted_data(
                        secret=dd.project.secret_key, salt=dd.project.get_salt()
                    ),
                )

    def test_questionnaire_response_encryption_default(self):
        # A participant has at most one QuestionnaireResponse per project, so
        # each iteration re-saves the same instance.
        qr = QuestionnaireResponse(
            project=self.base_project, participant=self.base_participant
        )
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                qr.data = raw_data
                qr.save()
                self.assertNotEqual(raw_data, qr.data)
                self.assertEqual(
                    raw_data,
                    qr.get_decrypted_data(
                        secret=qr.project.secret_key, salt=qr.project.get_salt()
                    ),
                )

    def test_data_donation_encryption_super_secret(self):
        # A participant has at most one DataDonation per blueprint, so each
        # iteration re-saves the same instance.
        dd = DataDonation(
            project=self.alt_project,
            blueprint=self.alt_blueprint,
            participant=self.alt_participant,
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
        )
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                dd.data = raw_data
                dd.save()
                self.assertNotEqual(raw_data, dd.data)
                with self.assertRaises(ValueError):
                    dd.get_decrypted_data(
                        secret="invalidSecret1234", salt=dd.project.get_salt()
                    )
                self.assertEqual(
                    raw_data,
                    dd.get_decrypted_data(
                        secret="test1234", salt=dd.project.get_salt()
                    ),
                )

    def test_questionnaire_response_encryption_super_secret(self):
        # See test_questionnaire_response_encryption_default: re-save the
        # same instance rather than creating a new row per raw_data value.
        qr = QuestionnaireResponse(
            project=self.alt_project, participant=self.alt_participant
        )
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                qr.data = raw_data
                qr.save()
                self.assertNotEqual(raw_data, qr.data)
                with self.assertRaises(ValueError):
                    qr.get_decrypted_data(
                        secret="invalidSecret1234", salt=qr.project.get_salt()
                    )
                self.assertEqual(
                    raw_data,
                    qr.get_decrypted_data(
                        secret="test1234", salt=qr.project.get_salt()
                    ),
                )

    def test_data_donation_encryption_with_provided_encryptor(self):
        # Built from an explicit (secret, salt) pair, independently of
        # whatever key material base_project itself actually uses - this
        # test is about save(encryptor=...) honoring a caller-supplied
        # Encryption instance, not about the project's own default key.
        secret, salt = self.base_project.secret_key, self.base_project.get_salt()
        encryptor = Encryption(secret=secret, salt=salt)
        decryptor = Decryption(secret=secret, salt=salt)
        # A participant has at most one DataDonation per blueprint, so each
        # iteration re-saves the same instance.
        dd = DataDonation(
            project=self.base_project,
            blueprint=self.base_blueprint,
            participant=self.base_participant,
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
        )
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                dd.data = raw_data
                dd.save(encryptor=encryptor)
                self.assertNotEqual(raw_data, dd.data)
                self.assertEqual(
                    raw_data,
                    dd.get_decrypted_data(secret=None, salt=None, decryptor=decryptor),
                )

    def test_data_donation_decryption_with_provided_decryptor(self):
        decryptor = self.base_project.get_decryptor()
        # A participant has at most one DataDonation per blueprint, so each
        # iteration re-saves the same instance.
        dd = DataDonation(
            project=self.base_project,
            blueprint=self.base_blueprint,
            participant=self.base_participant,
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
        )
        for raw_data in [self.raw_data_short, self.raw_data_long]:
            with self.subTest(raw_data=raw_data):
                dd.data = raw_data
                dd.save()
                self.assertNotEqual(raw_data, dd.data)
                self.assertEqual(
                    raw_data,
                    dd.get_decrypted_data(secret=None, salt=None, decryptor=decryptor),
                )

    def test_model_with_encryption_double_save(self):
        dd = DataDonation.objects.create(
            project=self.base_project,
            blueprint=self.base_blueprint,
            participant=self.base_participant,
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            data=self.raw_data_long,
        )
        dd.consent = False
        dd.save()
        self.assertFalse(dd.consent)
