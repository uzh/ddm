from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.datadonation.schemas import JSONParserConfig
from ddm.encryption.models import Encryption
from ddm.logging.models import ExceptionLogEntry
from ddm.participation.models import Participant
from ddm.projects.models import (
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_PRIMARY_COLOR,
    DonationProject,
    ResearchProfile,
)

User = get_user_model()


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestDonationProject(TestCase):
    @classmethod
    def setUpTestData(cls):
        credentials = {"username": "no_prof", "password": "123", "email": "u@mail.com"}
        cls.user = User.objects.create_user(**credentials)
        cls.user_profile = ResearchProfile.objects.create(user=cls.user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=cls.user_profile
        )

    def test_project_owner_cannot_be_null_on_create(self):
        invalid_project = DonationProject(name="test_project", slug="test")
        self.assertRaises(ValidationError, invalid_project.save)

    def test_get_statistics(self):
        statistics_keys = [
            "n_started",
            "n_completed",
            "completion_rate",
            "n_donations",
            "n_donated_files",
            "n_errors",
            "average_time",
        ]
        for key in statistics_keys:
            self.assertIn(key, self.project.get_statistics())

    def test_get_statistics_distinguishes_donations_from_donated_files(self):
        participant_a = Participant.objects.create(
            project=self.project, start_time=timezone.now()
        )
        participant_b = Participant.objects.create(
            project=self.project, start_time=timezone.now()
        )
        blueprint_a = DonationBlueprint.objects.create(
            project=self.project,
            name="blueprint_a",
            display_name="Blueprint A",
            expected_fields='"a"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )
        blueprint_b = DonationBlueprint.objects.create(
            project=self.project,
            name="blueprint_b",
            display_name="Blueprint B",
            expected_fields='"a"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )

        # participant_a donates to both blueprints, participant_b to one.
        for blueprint in (blueprint_a, blueprint_b):
            DataDonation.objects.create(
                project=self.project,
                blueprint=blueprint,
                participant=participant_a,
                time_submitted=timezone.now(),
                consent=True,
                data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
                n_data_entries=1,
                data=["entry"],
            )
        DataDonation.objects.create(
            project=self.project,
            blueprint=blueprint_a,
            participant=participant_b,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=1,
            data=["entry"],
        )
        # A non-extracted donation must not count toward either number.
        DataDonation.objects.create(
            project=self.project,
            blueprint=blueprint_a,
            participant=participant_b,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.FAILED,
            n_data_entries=0,
            data=[],
        )

        statistics = self.project.get_statistics()
        self.assertEqual(statistics["n_donations"], 2)
        self.assertEqual(statistics["n_donated_files"], 3)

    def test_get_statistics_excludes_test_participants(self):
        real_participant = Participant.objects.create(
            project=self.project, start_time=timezone.now(), completed=True
        )
        test_participant = Participant.objects.create(
            project=self.project,
            start_time=timezone.now(),
            completed=True,
            is_test=True,
        )
        blueprint = DonationBlueprint.objects.create(
            project=self.project,
            name="blueprint_a",
            display_name="Blueprint A",
            expected_fields='"a"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )
        DataDonation.objects.create(
            project=self.project,
            blueprint=blueprint,
            participant=real_participant,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=1,
            data=["entry"],
        )
        DataDonation.objects.create(
            project=self.project,
            blueprint=blueprint,
            participant=test_participant,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=1,
            data=["entry"],
        )
        ExceptionLogEntry.objects.create(
            project=self.project,
            participant=test_participant,
            exception_type="TestError",
            message="raised by a test run",
        )

        statistics = self.project.get_statistics()
        self.assertEqual(statistics["n_started"], 1)
        self.assertEqual(statistics["n_completed"], 1)
        self.assertEqual(statistics["n_donations"], 1)
        self.assertEqual(statistics["n_donated_files"], 1)
        self.assertEqual(statistics["n_errors"], 0)

        status_counts = self.project.get_blueprint_donation_status_counts()
        self.assertEqual(status_counts[0]["counts"], [1, 0, 0, 0])

    def test_get_blueprint_donation_status_counts(self):
        blueprint_a = DonationBlueprint.objects.create(
            project=self.project,
            name="blueprint_a",
            display_name="Blueprint A",
            display_position=1,
            expected_fields='"a"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )
        _ = DonationBlueprint.objects.create(
            project=self.project,
            name="blueprint_b",
            display_name="Blueprint B",
            display_position=2,
            expected_fields='"a"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )
        participant = Participant.objects.create(
            project=self.project, start_time=timezone.now()
        )

        DataDonation.objects.create(
            project=self.project,
            blueprint=blueprint_a,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=1,
            data=["entry"],
        )
        DataDonation.objects.create(
            project=self.project,
            blueprint=blueprint_a,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.FAILED,
            n_data_entries=0,
            data=[],
        )
        # blueprint_b has no donations at all.
        # An orphaned donation (blueprint deleted) must surface in its own row.
        orphaned = DataDonation.objects.create(
            project=self.project,
            blueprint=blueprint_a,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.NOT_ATTEMPTED,
            n_data_entries=0,
            data=[],
        )
        orphaned.blueprint = None
        orphaned.save(update_fields=["blueprint"])

        results = self.project.get_blueprint_donation_status_counts()

        by_blueprint_name = {
            row["blueprint"].name if row["blueprint"] else None: row["counts"]
            for row in results
        }
        # counts order: [DATA_EXTRACTED, NO_DATA_EXTRACTED, NOT_ATTEMPTED, FAILED]
        self.assertEqual(by_blueprint_name["blueprint_a"], [1, 0, 0, 1])
        self.assertEqual(by_blueprint_name["blueprint_b"], [0, 0, 0, 0])
        self.assertEqual(by_blueprint_name[None], [0, 0, 1, 0])

        # blueprint_a appears before blueprint_b (display_position order),
        # and the orphaned row comes last.
        ordered_names = [
            row["blueprint"].name if row["blueprint"] else None for row in results
        ]
        self.assertEqual(ordered_names, ["blueprint_a", "blueprint_b", None])

    def test_create_url_id(self):
        new_project = DonationProject.objects.create(
            name="test project", slug="test", owner=self.user_profile
        )
        self.assertIsNotNone(new_project.url_id)
        self.assertEqual(len(new_project.url_id), 8)

    def test_color_fields_default_to_theme_defaults(self):
        self.assertEqual(self.project.primary_color, DEFAULT_PRIMARY_COLOR)
        self.assertEqual(self.project.background_color, DEFAULT_BACKGROUND_COLOR)

    def test_has_custom_theme_false_by_default(self):
        self.assertFalse(self.project.has_custom_theme)

    def test_has_custom_theme_true_once_primary_color_changed(self):
        self.project.primary_color = "#aa3377"
        self.assertTrue(self.project.has_custom_theme)

    def test_has_custom_theme_true_once_background_color_changed(self):
        self.project.background_color = "#fdf3e7"
        self.assertTrue(self.project.has_custom_theme)

    def test_invalid_primary_color_rejected_by_full_clean(self):
        self.project.primary_color = "not-a-color"
        self.assertRaises(ValidationError, self.project.full_clean)

    def test_invalid_background_color_rejected_by_full_clean(self):
        self.project.background_color = "not-a-color"
        self.assertRaises(ValidationError, self.project.full_clean)

    def test_theme_version_reflects_current_colors(self):
        self.project.primary_color = "#aa3377"
        self.project.background_color = "#fdf3e7"
        self.assertEqual(self.project.theme_version, "aa3377fdf3e7")

    def test_theme_version_changes_when_a_color_changes(self):
        version_before = self.project.theme_version
        self.project.primary_color = "#aa3377"
        self.assertNotEqual(self.project.theme_version, version_before)

    def test_regenerate_test_token_changes_token(self):
        old_token = self.project.test_token
        self.project.regenerate_test_token()
        self.project.refresh_from_db()
        self.assertNotEqual(self.project.test_token, old_token)

    def test_two_projects_get_distinct_test_tokens(self):
        other = DonationProject.objects.create(
            name="Other Project", slug="other", owner=self.user_profile
        )
        self.assertNotEqual(self.project.test_token, other.test_token)


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestDonationProjectEncryption(TestCase):
    """
    Covers the per-project key material introduced in v3:
    a standard project created from now on gets its own randomly generated
    RSA key (wrapped at rest with a SECRET_KEY-derived key), while
    super_secret projects and any project that predates this field keep
    using the legacy on-the-fly derivation.
    """

    @classmethod
    def setUpTestData(cls):
        credentials = {
            "username": "enc_owner",
            "password": "123",
            "email": "enc_owner@mail.com",
        }
        cls.user = User.objects.create_user(**credentials)
        cls.user_profile = ResearchProfile.objects.create(user=cls.user)

    def test_standard_project_gets_wrapped_private_key_on_create(self):
        project = DonationProject.objects.create(
            name="Standard", slug="standard-enc", owner=self.user_profile
        )
        self.assertIsNotNone(project.wrapped_private_key)
        self.assertTrue(bytes(project.wrapped_private_key))

    def test_super_secret_project_never_gets_wrapped_private_key(self):
        project = DonationProject.objects.create(
            name="Secret",
            slug="secret-enc",
            owner=self.user_profile,
            super_secret=True,
            secret_key="a real secret",
        )
        self.assertFalse(project.wrapped_private_key)

    def test_wrapped_private_key_unchanged_on_second_save(self):
        project = DonationProject.objects.create(
            name="Standard2", slug="standard-enc-2", owner=self.user_profile
        )
        first = bytes(project.wrapped_private_key)
        project.name = "Standard2 renamed"
        project.save()
        self.assertEqual(bytes(project.wrapped_private_key), first)

    def test_get_decryptor_round_trips_for_new_standard_project(self):
        project = DonationProject.objects.create(
            name="Standard3", slug="standard-enc-3", owner=self.user_profile
        )
        encryptor = Encryption(public=project.public_key)
        ciphertext = encryptor.encrypt("hello")
        self.assertEqual(project.get_decryptor().decrypt(ciphertext), "hello")

    def test_get_decryptor_round_trips_for_super_secret_project(self):
        project = DonationProject.objects.create(
            name="Secret2",
            slug="secret-enc-2",
            owner=self.user_profile,
            super_secret=True,
            secret_key="correct secret",
        )
        encryptor = Encryption(public=project.public_key)
        ciphertext = encryptor.encrypt("hello")
        self.assertEqual(
            project.get_decryptor(secret="correct secret").decrypt(ciphertext),
            "hello",
        )
        with self.assertRaises(ValueError):
            project.get_decryptor(secret="wrong secret").decrypt(ciphertext)

    def test_get_decryptor_falls_back_to_legacy_derivation_for_pre_existing_project(
        self,
    ):
        """Simulates a project created before `wrapped_private_key` existed."""
        project = DonationProject.objects.create(
            name="Legacy", slug="legacy-enc", owner=self.user_profile
        )
        # Reproduce what a pre-migration row looked like: public_key derived
        # from (secret, date_created), wrapped_private_key empty.
        project.wrapped_private_key = None
        project.public_key = Encryption.get_public_key(
            project.secret, str(project.date_created)
        )
        project.save()

        encryptor = Encryption(public=project.public_key)
        ciphertext = encryptor.encrypt("hello")
        self.assertEqual(project.get_decryptor().decrypt(ciphertext), "hello")
