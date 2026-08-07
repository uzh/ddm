from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.datadonation.models import (
    BlueprintFilePath,
    DonationBlueprint,
    ExtractionField,
    FileUploader,
    ProcessingRule,
)
from ddm.datadonation.schemas import JSONParserConfig
from ddm.datadonation.services import copy_blueprint
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class TestCopyBlueprint(TestCase):
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
            parser_config=JSONParserConfig().model_dump(),
        )
        cls.field_a = ExtractionField.objects.create(
            blueprint=cls.blueprint,
            expected_name="fieldA",
        )
        cls.field_b = ExtractionField.objects.create(
            blueprint=cls.blueprint,
            expected_name="fieldB",
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
        BlueprintFilePath.objects.create(
            path="/this/file.json",
            is_regex=True,
            blueprint=cls.blueprint,
        )

    def test_creates_new_blueprint_with_distinct_pk_and_suffixed_name(self):
        new_bp = copy_blueprint(self.blueprint)
        self.assertNotEqual(new_bp.pk, self.blueprint.pk)
        self.assertEqual(new_bp.name, "test_blueprint_copy")

    def test_original_blueprint_untouched(self):
        copy_blueprint(self.blueprint)
        self.blueprint.refresh_from_db()
        self.assertEqual(self.blueprint.name, "test_blueprint")
        self.assertEqual(self.blueprint.extractionfield_set.count(), 2)

    def test_copies_file_paths_to_new_blueprint(self):
        new_bp = copy_blueprint(self.blueprint)
        self.assertEqual(new_bp.blueprintfilepath_set.count(), 1)
        copied_fp = new_bp.blueprintfilepath_set.first()
        self.assertEqual(copied_fp.path, "/this/file.json")
        self.assertTrue(copied_fp.is_regex)
        self.assertNotIn(
            copied_fp.pk,
            self.blueprint.blueprintfilepath_set.values_list("pk", flat=True),
        )

    def test_copies_extraction_fields_and_relinks_them(self):
        new_bp = copy_blueprint(self.blueprint)
        self.assertEqual(new_bp.extractionfield_set.count(), 2)
        names = set(new_bp.extractionfield_set.values_list("expected_name", flat=True))
        self.assertEqual(names, {"fieldA", "fieldB"})
        # copied fields must be new rows, not the originals reassigned
        self.assertFalse(new_bp.extractionfield_set.filter(pk=self.field_a.pk).exists())

    def test_copies_processing_rules_and_relinks_to_new_field(self):
        new_bp = copy_blueprint(self.blueprint)
        new_field_a = new_bp.extractionfield_set.get(expected_name="fieldA")
        rules = new_field_a.processingrule_set.all()
        self.assertEqual(rules.count(), 1)
        rule = rules.first()
        self.assertEqual(rule.blueprint, new_bp)
        self.assertNotEqual(rule.field_id, self.field_a.pk)

    def test_repeated_copy_increments_suffix(self):
        copy_blueprint(self.blueprint)
        second_copy = copy_blueprint(self.blueprint)
        self.assertEqual(second_copy.name, "test_blueprint_copy_1")

    def test_copy_does_not_duplicate_processing_rules_across_fields(self):
        new_bp = copy_blueprint(self.blueprint)
        total_rules = ProcessingRule.objects.filter(blueprint=new_bp).count()
        self.assertEqual(total_rules, 2)  # one per field, not field_c (has none)
