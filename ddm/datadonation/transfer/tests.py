import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from ddm.core.utils.transfer.id_mapping import LocalIdAllocator
from ddm.datadonation.models import (
    BlueprintFilePath,
    DonationBlueprint,
    ExtractionField,
    FileUploader,
    ProcessingRule,
)
from ddm.datadonation.schemas import JSONParserConfig
from ddm.datadonation.transfer.services import (
    build_blueprint,
    copy_blueprint,
    export_blueprint,
    serialize_blueprint,
)
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class TestSerializeBlueprint(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Project", slug="project", owner=profile
        )
        cls.uploader = FileUploader.objects.create(
            project=cls.project, name="uploader", upload_type="single file"
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            file_uploader=cls.uploader,
            name="bp",
            expected_fields='"a"',
            parser_config=JSONParserConfig().model_dump(),
        )
        cls.field = ExtractionField.objects.create(
            blueprint=cls.blueprint, expected_name="a"
        )
        ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name="rule",
            field=cls.field,
            execution_order=1,
            comparison_operator=ProcessingRule.ComparisonOperators.EQUAL,
        )
        BlueprintFilePath.objects.create(blueprint=cls.blueprint, path="/f.json")

    def test_file_uploader_ref_omitted_by_default(self):
        data = serialize_blueprint(self.blueprint, LocalIdAllocator())
        self.assertIsNone(data["file_uploader_local_id"])

    def test_file_uploader_ref_included_when_requested(self):
        allocator = LocalIdAllocator()
        data = serialize_blueprint(
            self.blueprint, allocator, include_file_uploader_ref=True
        )
        self.assertIsNotNone(data["file_uploader_local_id"])

    def test_nested_config_serialized(self):
        data = serialize_blueprint(self.blueprint, LocalIdAllocator())
        self.assertEqual(len(data["extraction_fields"]), 1)
        self.assertEqual(len(data["processing_rules"]), 1)
        self.assertEqual(len(data["file_paths"]), 1)
        self.assertEqual(
            data["processing_rules"][0]["field_local_id"],
            data["extraction_fields"][0]["local_id"],
        )


class TestBuildBlueprintStandalone(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.source_project = DonationProject.objects.create(
            name="Source", slug="source", owner=profile
        )
        cls.target_project = DonationProject.objects.create(
            name="Target", slug="target", owner=profile
        )
        cls.target_uploader = FileUploader.objects.create(
            project=cls.target_project,
            name="target uploader",
            upload_type="single file",
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.source_project,
            name="shared_name",
            display_name="Shared Name",
            expected_fields='"a"',
            parser_config=JSONParserConfig().model_dump(),
        )
        field = ExtractionField.objects.create(
            blueprint=cls.blueprint, expected_name="a"
        )
        ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name="rule",
            field=field,
            execution_order=1,
            comparison_operator=ProcessingRule.ComparisonOperators.EQUAL,
        )

    def test_imports_into_different_project(self):
        data = serialize_blueprint(self.blueprint, LocalIdAllocator())
        new_bp = build_blueprint(data, self.target_project)
        self.assertEqual(new_bp.project, self.target_project)
        self.assertEqual(new_bp.name, "shared_name")
        self.assertEqual(new_bp.extractionfield_set.count(), 1)
        self.assertEqual(new_bp.processingrule_set.count(), 1)

    def test_no_collision_across_different_projects(self):
        # A blueprint with the same name already exists in the SOURCE
        # project; importing into a DIFFERENT (empty) target project must
        # not be suffixed just because that name exists somewhere else.
        data = serialize_blueprint(self.blueprint, LocalIdAllocator())
        new_bp = build_blueprint(data, self.target_project)
        self.assertEqual(new_bp.name, "shared_name")

    def test_collision_within_target_project_is_suffixed(self):
        DonationBlueprint.objects.create(
            project=self.target_project,
            name="shared_name",
            display_name="Shared Name",
            expected_fields='"a"',
            parser_config=JSONParserConfig().model_dump(),
        )
        data = serialize_blueprint(self.blueprint, LocalIdAllocator())
        new_bp = build_blueprint(data, self.target_project)
        self.assertEqual(new_bp.name, "shared_name_1")

    def test_optional_file_uploader_attachment(self):
        data = serialize_blueprint(self.blueprint, LocalIdAllocator())
        new_bp = build_blueprint(
            data, self.target_project, file_uploader=self.target_uploader
        )
        self.assertEqual(new_bp.file_uploader, self.target_uploader)

    def test_no_file_uploader_attachment_by_default(self):
        data = serialize_blueprint(self.blueprint, LocalIdAllocator())
        new_bp = build_blueprint(data, self.target_project)
        self.assertIsNone(new_bp.file_uploader)

    def test_backup_for_is_none_when_backup_not_in_same_import(self):
        backup = DonationBlueprint.objects.create(
            project=self.source_project,
            name="backup",
            display_name="Backup",
            backup_for=self.blueprint,
            expected_fields='"a"',
            parser_config=JSONParserConfig().model_dump(),
        )
        # Exporting ONLY the backup, not its primary.
        data = serialize_blueprint(backup, LocalIdAllocator())
        new_backup = build_blueprint(data, self.target_project)
        self.assertIsNone(new_backup.backup_for)


class TestCopyBlueprint(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="copyowner", password="123", email="copyowner@mail.com"
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


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestBlueprintExportImportViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner)

        cls.source_project = DonationProject.objects.create(
            name="Source", slug="source", owner=cls.owner_profile
        )
        cls.target_project = DonationProject.objects.create(
            name="Target", slug="target", owner=cls.owner_profile
        )
        cls.target_uploader = FileUploader.objects.create(
            project=cls.target_project, name="uploader", upload_type="single file"
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.source_project,
            name="bp",
            display_name="BP",
            expected_fields='"a"',
            parser_config=JSONParserConfig().model_dump(),
        )

    def test_export_returns_downloadable_json(self):
        self.client.login(username="owner", password="123")
        response = self.client.get(
            reverse(
                "ddm_datadonation:blueprints:export",
                args=[self.source_project.url_id, self.blueprint.pk],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        data = json.loads(response.content)
        self.assertEqual(data["export_kind"], "blueprint")

    def test_import_into_different_project(self):
        self.client.login(username="owner", password="123")
        payload = export_blueprint(self.blueprint)
        raw = json.dumps(payload).encode("utf-8")
        upload = SimpleUploadedFile("bp.json", raw, content_type="application/json")

        response = self.client.post(
            reverse(
                "ddm_datadonation:blueprints:import", args=[self.target_project.url_id]
            ),
            data={"file": upload, "file_uploader": self.target_uploader.pk},
        )
        self.assertEqual(response.status_code, 302)
        new_bp = self.target_project.donationblueprint_set.get(name="bp")
        self.assertEqual(new_bp.file_uploader, self.target_uploader)
