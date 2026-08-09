from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

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
            "n_errors",
            "average_time",
        ]
        for key in statistics_keys:
            self.assertIn(key, self.project.get_statistics())

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
