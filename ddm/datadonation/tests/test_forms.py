from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.datadonation.forms import BlueprintForm, FileUploaderForm
from ddm.datadonation.models import FileUploader, DonationBlueprint
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class TestBlueprintForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name='zip file uploader',
            upload_type=FileUploader.UploadTypes.ZIP_FILE
        )

    def test_valid(self):
        bp = DonationBlueprint.objects.create(
            project=self.file_uploader.project,
            name='valid blueprint',
            display_name='some name',
            description='some description',
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
        )
        data = {
            'name': bp.name,
            'display_name': bp.display_name,
            'description': bp.description,
            'display_position': bp.display_position,
            'exp_file_format': 'json',
            'csv_delimiter': bp.csv_delimiter,
            'file_uploader': bp.file_uploader.pk,
            'json_extraction_root': bp.json_extraction_root,
            'expected_fields': bp.expected_fields,
            'expected_fields_regex_matching': bp.expected_fields_regex_matching,
        }
        form = BlueprintForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_missing_attribute(self):
        """New data is missing display_position attribute."""
        bp = DonationBlueprint.objects.create(
            project=self.file_uploader.project,
            name='valid blueprint',
            display_name='some name',
            description='some description',
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
        )
        data = {
            'name': 'different name',
            'display_name': bp.display_name,
            'description': bp.description,
            'exp_file_format': 'json',
            'csv_delimiter': bp.csv_delimiter,
            'file_uploader': bp.file_uploader.pk,
            'json_extraction_root': bp.json_extraction_root,
            'expected_fields': bp.expected_fields,
            'expected_fields_regex_matching': bp.expected_fields_regex_matching,
        }
        form = BlueprintForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_already_existing_name(self):
        bp = DonationBlueprint.objects.create(
            project=self.file_uploader.project,
            name='valid blueprint',
            display_name='some name',
            description='some description',
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
        )
        data = {
            'name': bp.name,
            'display_name': bp.display_name,
            'description': bp.description,
            'display_position': bp.display_position,
            'exp_file_format': 'json',
            'csv_delimiter': bp.csv_delimiter,
            'file_uploader': bp.file_uploader.pk,
            'json_extraction_root': bp.json_extraction_root,
            'expected_fields': bp.expected_fields,
            'expected_fields_regex_matching': bp.expected_fields_regex_matching,
        }
        form = BlueprintForm(data=data, project=self.project)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class TestFileUploaderForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

        cls.uploader = FileUploader.objects.create(
            project=cls.project,
            name='zip file uploader',
            upload_type=FileUploader.UploadTypes.ZIP_FILE
        )

    def test_invalid_already_existing_name(self):
        data = {
            'name': self.uploader.name,
            'display_name': self.uploader.display_name,
            'index': 1,
            'upload_type': self.uploader.upload_type,
        }
        form = FileUploaderForm(data=data, project=self.project)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
