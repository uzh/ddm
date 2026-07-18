from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ddm.datadonation.models import (
    BlueprintFilePath,
    DataDonation,
    DonationBlueprint,
    DonationInstruction,
    ExtractionField,
    FileUploader,
    ProcessingRule,
)
from ddm.logging.models import ExceptionLogEntry
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class TestDonationInstructionModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)

        project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )

        cls.file_uploader = FileUploader.objects.create(
            project=project,
            name="basic file uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )

    def setUp(self):
        self.instruction_2 = DonationInstruction.objects.create(
            text="instruction 2", index=2, file_uploader=self.file_uploader
        )
        self.instruction_3 = DonationInstruction.objects.create(
            text="instruction 3", index=3, file_uploader=self.file_uploader
        )

    def test_create_with_existing_index_pushes_other_indices(self):
        new_instruction = DonationInstruction.objects.create(
            text="instruction new", index=2, file_uploader=self.file_uploader
        )
        self.assertEqual(new_instruction.index, 2)

        self.instruction_2.refresh_from_db()
        self.assertEqual(self.instruction_2.index, 3)

        self.instruction_3.refresh_from_db()
        self.assertEqual(self.instruction_3.index, 4)

    def test_decrease_index_of_existing_instruction(self):
        self.instruction_3.index = 2
        self.instruction_3.save()
        self.assertEqual(self.instruction_3.index, 2)

        self.instruction_2.refresh_from_db()
        self.assertEqual(self.instruction_2.index, 3)

    def test_increase_index_of_existing_instruction(self):
        self.instruction_2.index = 3
        self.instruction_2.save()
        self.assertEqual(self.instruction_2.index, 3)

        self.instruction_3.refresh_from_db()
        self.assertEqual(self.instruction_3.index, 2)

    def test_indices_are_adjusted_on_delete(self):
        self.instruction_2.delete()

        self.instruction_3.refresh_from_db()
        self.assertEqual(self.instruction_3.index, 2)

    def test_clean(self):
        instruction_in_db = DonationInstruction.objects.create(
            text="instruction", index=20, file_uploader=self.file_uploader
        )
        instruction_not_in_db = DonationInstruction(
            text="instruction", index=21, file_uploader=self.file_uploader
        )
        with self.assertRaises(ValidationError):
            instruction_in_db.clean()
            instruction_not_in_db.clean()


class TestDonationBlueprintModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)

        project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )

        cls.file_uploader = FileUploader.objects.create(
            project=project,
            name="basic file uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=project,
            name="valid blueprint",
            description="some description",
            expected_fields='"some field"',
            file_uploader=cls.file_uploader,
        )

        cls.participant = Participant.objects.create(
            project=project, start_time=timezone.now()
        )

        cls.field_a = ExtractionField.objects.create(
            blueprint=cls.blueprint,
            expected_name="fieldA",
        )

        cls.field_b = ExtractionField.objects.create(
            blueprint=cls.blueprint,
            expected_name="fieldB",
        )

        cls.field_c = ExtractionField.objects.create(
            blueprint=cls.blueprint,
            expected_name="fieldC",
        )

        ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name="",
            field=cls.field_a,
            execution_order=1,
        )

        ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name="",
            field=cls.field_b,
            execution_order=2,
            comparison_operator=ProcessingRule.ComparisonOperators.EQUAL,
        )

        ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name="",
            field=cls.field_c,
            execution_order=3,
        )

    def test_get_slug(self):
        self.assertEqual(self.blueprint.get_slug(), "blueprint")

    def test_validate_donation_case_valid(self):
        data = {
            "consent": True,
            "extractedData": ["some data"],
            "status": "DATA_EXTRACTED",
        }
        self.assertTrue(self.blueprint.validate_donation(data))

    def test_validate_donation_case_invalid(self):
        data = {
            "consent": True,
            "extractedData": ["some data"],
        }
        self.assertFalse(self.blueprint.validate_donation(data))

    def test_process_donation_case_valid(self):
        data = {
            "consent": True,
            "extractedData": ["some data"],
            "status": "DATA_EXTRACTED",
        }
        n_donations_pre = DataDonation.objects.count()
        self.blueprint.process_donation(data, self.participant)
        n_donations_post = DataDonation.objects.count()
        self.assertEqual(n_donations_post - n_donations_pre, 1)

    def test_process_donation_case_invalid(self):
        data = {
            "consent": True,
            "extractedData": ["some data"],
        }
        n_donations_pre = DataDonation.objects.count()
        n_exceptions_pre = ExceptionLogEntry.objects.count()

        self.blueprint.process_donation(data, self.participant)

        n_donations_post = DataDonation.objects.count()
        n_exceptions_post = ExceptionLogEntry.objects.count()

        self.assertEqual(n_donations_post - n_donations_pre, 0)
        self.assertEqual(n_exceptions_post - n_exceptions_pre, 2)


class TestDonationBlueprintRegexValidation(TestCase):
    """Tests for regex validation in DonationBlueprint.clean()."""

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base-regex", owner=profile
        )
        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name="basic file uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )

    def test_valid_expected_fields_regex_passes(self):
        blueprint = DonationBlueprint(
            project=self.project,
            name="test blueprint",
            expected_fields=r'"field_\d+", "other_[a-z]+"',
            expected_fields_regex_matching=True,
            file_uploader=self.file_uploader,
        )
        blueprint.clean()  # Should not raise

    def test_invalid_expected_fields_regex_raises_error(self):
        blueprint = DonationBlueprint(
            project=self.project,
            name="test blueprint",
            expected_fields=r'"[unclosed"',
            expected_fields_regex_matching=True,
            file_uploader=self.file_uploader,
        )
        with self.assertRaises(ValidationError) as ctx:
            blueprint.clean()
        self.assertIn("expected_fields", ctx.exception.message_dict)

    def test_dangerous_expected_fields_regex_raises_error(self):
        blueprint = DonationBlueprint(
            project=self.project,
            name="test blueprint",
            expected_fields=r'"(a+)+"',
            expected_fields_regex_matching=True,
            file_uploader=self.file_uploader,
        )
        with self.assertRaises(ValidationError) as ctx:
            blueprint.clean()
        self.assertIn("expected_fields", ctx.exception.message_dict)

    def test_expected_fields_not_validated_when_regex_disabled(self):
        """When regex matching is disabled, patterns aren't validated as regex."""
        blueprint = DonationBlueprint(
            project=self.project,
            name="test blueprint",
            expected_fields=r'"[not a valid regex"',
            expected_fields_regex_matching=False,
            file_uploader=self.file_uploader,
        )
        blueprint.clean()  # Should not raise - not treated as regex


class TestBlueprintFilePath(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base-regex", owner=profile
        )
        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name="basic file uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name="test_blueprint",
            display_name="test blueprint",
            expected_fields='"field1"',
            file_uploader=cls.file_uploader,
        )

    def test_valid_regex_pattern_passes(self):
        path = BlueprintFilePath.objects.create(
            path="/this/file.json",
            is_regex=True,
            blueprint=self.blueprint,
        )
        path.clean()  # Should not raise

    def test_invalid_regex_pattern_syntax_raises_error(self):
        path = BlueprintFilePath.objects.create(
            path="[unclosed",
            is_regex=True,
            blueprint=self.blueprint,
        )

        with self.assertRaises(ValidationError) as ctx:
            path.clean()
        self.assertIn("path", ctx.exception.message_dict)

    def test_invalid_regex_pattern_does_not_raise_when_is_regex_false(self):
        path = BlueprintFilePath.objects.create(
            path="[unclosed",
            is_regex=False,
            blueprint=self.blueprint,
        )
        path.clean()  # should not raise

    def test_dangerous_regex_pattern_raises_error(self):
        path = BlueprintFilePath.objects.create(
            path="(a+)+",
            is_regex=True,
            blueprint=self.blueprint,
        )
        with self.assertRaises(ValidationError) as ctx:
            path.clean()
        self.assertIn("path", ctx.exception.message_dict)


class TestExtractionFieldRegexValidation(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner2", password="123", email="owner2@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        project = DonationProject.objects.create(
            name="Base Project 2", slug="base-regex-2", owner=profile
        )
        file_uploader = FileUploader.objects.create(
            project=project,
            name="basic file uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=project,
            name="valid blueprint",
            expected_fields='"field"',
            file_uploader=file_uploader,
        )

    def test_valid_regex_field_passes(self):
        field = ExtractionField(
            blueprint=self.blueprint,
            expected_name=r"field_\d+",
            match_regex=True,
        )
        field.clean()  # Should not raise

    def test_invalid_regex_field_no_regex_match_passes(self):
        field = ExtractionField(
            blueprint=self.blueprint,
            expected_name=r"[unclosed",
            match_regex=False,
        )
        field.clean()  # Should not raise

    def test_invalid_regex_field_syntax_raises_error(self):
        field = ExtractionField(
            blueprint=self.blueprint,
            expected_name=r"[unclosed",
            match_regex=True,
        )
        with self.assertRaises(ValidationError) as ctx:
            field.clean()
        self.assertIn("expected_name", ctx.exception.message_dict)

    def test_dangerous_regex_field_raises_error(self):
        field = ExtractionField(
            blueprint=self.blueprint,
            expected_name=r"(a+)+",
            match_regex=True,
        )
        with self.assertRaises(ValidationError) as ctx:
            field.clean()
        self.assertIn("expected_name", ctx.exception.message_dict)


class TestProcessingRuleRegexValidation(TestCase):
    """Tests for regex validation in ProcessingRule.clean()."""

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner2", password="123", email="owner2@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        project = DonationProject.objects.create(
            name="Base Project 2", slug="base-regex-2", owner=profile
        )
        file_uploader = FileUploader.objects.create(
            project=project,
            name="basic file uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=project,
            name="valid blueprint",
            expected_fields='"field"',
            file_uploader=file_uploader,
        )

        cls.field = ExtractionField(
            blueprint=cls.blueprint,
            expected_name="some_field",
        )

    def test_valid_regex_comparison_value_passes(self):
        rule = ProcessingRule(
            blueprint=self.blueprint,
            name="test rule",
            field=self.field,
            execution_order=1,
            comparison_operator=ProcessingRule.ComparisonOperators.REGEX_DELETE_MATCH,
            comparison_value=r"\d{4}-\d{2}-\d{2}",
        )
        rule.clean()  # Should not raise

    def test_invalid_regex_comparison_value_raises_error(self):
        rule = ProcessingRule(
            blueprint=self.blueprint,
            name="test rule",
            field=self.field,
            execution_order=1,
            comparison_operator=ProcessingRule.ComparisonOperators.REGEX_DELETE_MATCH,
            comparison_value=r"[unclosed",
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.clean()
        self.assertIn("comparison_value", ctx.exception.message_dict)

    def test_dangerous_regex_comparison_value_raises_error(self):
        rule = ProcessingRule(
            blueprint=self.blueprint,
            name="test rule",
            field=self.field,
            execution_order=1,
            comparison_operator=ProcessingRule.ComparisonOperators.REGEX_REPLACE_MATCH,
            comparison_value=r"(a+)+",
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.clean()
        self.assertIn("comparison_value", ctx.exception.message_dict)

    def test_comparison_value_not_validated_for_non_regex_operators(self):
        """Non-regex operators don't validate comparison_value as regex."""
        rule = ProcessingRule(
            blueprint=self.blueprint,
            name="test rule",
            field=self.field,
            execution_order=1,
            comparison_operator=ProcessingRule.ComparisonOperators.EQUAL,
            comparison_value=r"[not valid regex",
        )
        rule.clean()  # Should not raise

    def test_all_regex_operators_trigger_validation(self):
        """All three regex operators should trigger comparison_value validation."""
        regex_operators = [
            ProcessingRule.ComparisonOperators.REGEX_DELETE_MATCH,
            ProcessingRule.ComparisonOperators.REGEX_REPLACE_MATCH,
            ProcessingRule.ComparisonOperators.REGEX_DELETE_ROW,
        ]
        for operator in regex_operators:
            with self.subTest(operator=operator):
                rule = ProcessingRule(
                    blueprint=self.blueprint,
                    name="test rule",
                    field=self.field,
                    execution_order=1,
                    comparison_operator=operator,
                    comparison_value=r"[unclosed",
                )
                with self.assertRaises(ValidationError) as ctx:
                    rule.clean()
                self.assertIn("comparison_value", ctx.exception.message_dict)
