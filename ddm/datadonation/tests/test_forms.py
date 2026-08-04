from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.datadonation.forms import BlueprintForm, FileUploaderForm
from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.datadonation.schemas import JSONParserConfig, TXTParserConfig
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class TestBlueprintForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )

        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name="zip file uploader",
            upload_type=FileUploader.UploadTypes.ZIP_FILE,
        )

    def test_valid(self):
        bp = DonationBlueprint.objects.create(
            project=self.file_uploader.project,
            name="valid blueprint",
            display_name="some name",
            description="some description",
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
            parser_config=JSONParserConfig().model_dump(),
        )
        data = {
            "name": bp.name,
            "display_name": bp.display_name,
            "description": bp.description,
            "display_position": bp.display_position,
            "exp_file_format": "json",
            "json_extraction_root": "",
            "file_uploader": bp.file_uploader.pk,
            "expected_fields": bp.expected_fields,
            "expected_fields_regex_matching": bp.expected_fields_regex_matching,
        }
        form = BlueprintForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_missing_attribute(self):
        """New data is missing display_position attribute."""
        bp = DonationBlueprint.objects.create(
            project=self.file_uploader.project,
            name="valid blueprint",
            display_name="some name",
            description="some description",
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
            parser_config=JSONParserConfig().model_dump(),
        )
        data = {
            "name": "different name",
            "display_name": bp.display_name,
            "description": bp.description,
            "exp_file_format": "json",
            "json_extraction_root": "",
            "file_uploader": bp.file_uploader.pk,
            "expected_fields": bp.expected_fields,
            "expected_fields_regex_matching": bp.expected_fields_regex_matching,
        }
        form = BlueprintForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_already_existing_name(self):
        bp = DonationBlueprint.objects.create(
            project=self.file_uploader.project,
            name="valid blueprint",
            display_name="some name",
            description="some description",
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
            parser_config=JSONParserConfig().model_dump(),
        )
        data = {
            "name": bp.name,
            "display_name": bp.display_name,
            "description": bp.description,
            "display_position": bp.display_position,
            "exp_file_format": "json",
            "json_extraction_root": "",
            "file_uploader": bp.file_uploader.pk,
            "expected_fields": bp.expected_fields,
            "expected_fields_regex_matching": bp.expected_fields_regex_matching,
        }
        form = BlueprintForm(data=data, project=self.project)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_valid_csv(self):
        """CSV-specific fields are correctly assembled into parser_config."""
        data = {
            "name": "csv blueprint",
            "display_name": "some name",
            "description": "some description",
            "display_position": 1,
            "exp_file_format": "csv",
            "csv_delimiter": ";",
            "file_uploader": self.file_uploader.pk,
            "expected_fields": '"some field"',
            "expected_fields_regex_matching": False,
        }
        form = BlueprintForm(data=data, project=self.project)
        self.assertTrue(form.is_valid(), form.errors)
        bp = form.save()
        self.assertEqual(bp.parser_config, {"format": "csv", "delimiter": ";"})

    def test_valid_txt(self):
        """TXT-specific fields are correctly assembled into parser_config,
        including unescaping of literal \\n typed by the user."""
        data = {
            "name": "txt blueprint",
            "display_name": "some name",
            "description": "some description",
            "display_position": 1,
            "exp_file_format": "txt",
            "txt_record_separator": "\\n\\n",
            "txt_field_separator": "\\n",
            "txt_kv_separator": ":",
            "txt_skip_header_lines": 0,
            "txt_skip_footer_lines": 0,
            "txt_ignore_blank_lines": True,
            "txt_trim_whitespace": True,
            "file_uploader": self.file_uploader.pk,
            "expected_fields": '"Datum", "Link"',
            "expected_fields_regex_matching": False,
        }
        form = BlueprintForm(data=data, project=self.project)
        self.assertTrue(form.is_valid(), form.errors)
        bp = form.save()

        # Confirm the literal "\n" typed in the input was converted into
        # an actual newline character, not stored verbatim.
        self.assertEqual(bp.parser_config["record_separator"], "\n\n")
        self.assertEqual(bp.parser_config["field_separator"], "\n")
        self.assertEqual(bp.parser_config["format"], "txt")

    def test_txt_blank_optional_fields_fall_back_to_schema_defaults(self):
        """Leaving TXT fields blank should use TXTParserConfig defaults,
        not None/empty-string, and should not raise a validation error."""
        data = {
            "name": "txt defaults blueprint",
            "display_name": "some name",
            "description": "some description",
            "display_position": 1,
            "exp_file_format": "txt",
            "txt_record_separator": "",
            "txt_field_separator": "",
            "txt_kv_separator": "",
            "txt_skip_header_lines": "",
            "txt_skip_footer_lines": "",
            "txt_ignore_blank_lines": False,
            "txt_trim_whitespace": False,
            "file_uploader": self.file_uploader.pk,
            "expected_fields": '"some field"',
            "expected_fields_regex_matching": False,
        }
        form = BlueprintForm(data=data, project=self.project)
        self.assertTrue(form.is_valid(), form.errors)
        bp = form.save()

        defaults = TXTParserConfig()
        self.assertEqual(
            bp.parser_config["record_separator"], defaults.record_separator
        )
        self.assertEqual(
            bp.parser_config["skip_header_lines"], defaults.skip_header_lines
        )

    def test_invalid_txt_field_maps_to_correct_form_field(self):
        """A Pydantic validation error on a TXT schema field is attached to
        the corresponding prefixed form field, not as a generic error."""
        data = {
            "name": "bad txt blueprint",
            "display_name": "some name",
            "description": "some description",
            "display_position": 1,
            "exp_file_format": "txt",
            "txt_record_separator": "\\n\\n",
            "txt_field_separator": "\\n",
            "txt_kv_separator": ":",
            "txt_skip_header_lines": -1,  # invalid: min_value=0
            "txt_skip_footer_lines": 0,
            "txt_ignore_blank_lines": True,
            "txt_trim_whitespace": True,
            "file_uploader": self.file_uploader.pk,
            "expected_fields": '"some field"',
            "expected_fields_regex_matching": False,
        }
        form = BlueprintForm(data=data, project=self.project)
        self.assertFalse(form.is_valid())
        self.assertIn("txt_skip_header_lines", form.errors)

    def test_edit_existing_txt_blueprint_prefills_escaped_values(self):
        """When editing an existing TXT blueprint, the form's initial values
        show literal \\n (escaped) rather than a raw embedded newline."""
        bp = DonationBlueprint.objects.create(
            project=self.project,
            name="existing txt blueprint",
            display_name="some name",
            description="some description",
            expected_fields='"Datum", "Link"',
            file_uploader=self.file_uploader,
            exp_file_format="txt",
            parser_config=TXTParserConfig(
                record_separator="\n\n", field_separator="\n"
            ).model_dump(),
        )
        form = BlueprintForm(instance=bp, project=self.project)
        self.assertEqual(form.fields["txt_record_separator"].initial, "\\n\\n")
        self.assertEqual(form.fields["txt_field_separator"].initial, "\\n")

    def test_switching_format_replaces_parser_config_entirely(self):
        """Switching a blueprint from json to txt should fully replace
        parser_config, leaving no stale JSON-specific keys behind."""
        bp = DonationBlueprint.objects.create(
            project=self.project,
            name="switching blueprint",
            display_name="some name",
            description="some description",
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
            exp_file_format="json",
            parser_config=JSONParserConfig(extraction_root="root.path").model_dump(),
        )
        data = {
            "name": bp.name,
            "display_name": bp.display_name,
            "description": bp.description,
            "display_position": bp.display_position,
            "exp_file_format": "txt",
            "txt_record_separator": "\\n\\n",
            "txt_field_separator": "\\n",
            "txt_kv_separator": ":",
            "txt_skip_header_lines": 0,
            "txt_skip_footer_lines": 0,
            "txt_ignore_blank_lines": True,
            "txt_trim_whitespace": True,
            "file_uploader": bp.file_uploader.pk,
            "expected_fields": bp.expected_fields,
            "expected_fields_regex_matching": bp.expected_fields_regex_matching,
        }
        form = BlueprintForm(data=data, instance=bp, project=self.project)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()

        self.assertEqual(saved.parser_config["format"], "txt")
        self.assertNotIn("extraction_root", saved.parser_config)

    def test_name_uniqueness_allows_same_name_across_projects(self):
        """The uniqueness check is scoped per-project via the project kwarg;
        omitting project (as some existing tests do) should skip that check
        entirely rather than raise."""
        DonationBlueprint.objects.create(
            project=self.project,
            name="shared name",
            display_name="some name",
            description="some description",
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
            parser_config=JSONParserConfig().model_dump(),
        )
        data = {
            "name": "shared name",
            "display_name": "another name",
            "description": "some description",
            "display_position": 1,
            "exp_file_format": "json",
            "json_extraction_root": "",
            "file_uploader": self.file_uploader.pk,
            "expected_fields": '"some field"',
            "expected_fields_regex_matching": False,
        }
        # No `project=` passed -> uniqueness check is skipped by design.
        form = BlueprintForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)


class TestFileUploaderForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )

        cls.uploader = FileUploader.objects.create(
            project=cls.project,
            name="zip file uploader",
            upload_type=FileUploader.UploadTypes.ZIP_FILE,
        )

    def test_invalid_already_existing_name(self):
        data = {
            "name": self.uploader.name,
            "display_name": self.uploader.display_name,
            "index": 1,
            "upload_type": self.uploader.upload_type,
        }
        form = FileUploaderForm(data=data, project=self.project)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
