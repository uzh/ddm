from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.datadonation.forms import BlueprintEditForm
from ddm.datadonation.models import FileUploader, DonationBlueprint
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class TestBlueprintEditForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)

        project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

        cls.file_uploader = FileUploader.objects.create(
            project=project,
            name='zip file uploader',
            upload_type=FileUploader.UploadTypes.ZIP_FILE
        )

    def test_valid(self):
        bp = DonationBlueprint.objects.create(
            project=self.file_uploader.project,
            name='valid blueprint',
            description='some description',
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
            regex_path='/this/file.json'
        )
        data = {
            'name': bp.name,
            'description': bp.description,
            'regex_path': bp.regex_path,
            'exp_file_format': 'json',
            'csv_delimiter': bp.csv_delimiter,
            'file_uploader': bp.file_uploader.pk,
            'json_extraction_root': bp.json_extraction_root,
            'expected_fields': bp.expected_fields,
            'expected_fields_regex_matching': bp.expected_fields_regex_matching,
        }
        form = BlueprintEditForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid(self):
        bp = DonationBlueprint.objects.create(
            project=self.file_uploader.project,
            name='valid blueprint',
            description='some description',
            expected_fields='"some field"',
            file_uploader=self.file_uploader,
            regex_path='/this/file.json'
        )
        data = {
            'name': bp.name,
            'description': bp.description,
            'regex_path': '',
            'exp_file_format': 'json',
            'csv_delimiter': bp.csv_delimiter,
            'file_uploader': bp.file_uploader.pk,
            'json_extraction_root': bp.json_extraction_root,
            'expected_fields': bp.expected_fields,
            'expected_fields_regex_matching': bp.expected_fields_regex_matching,
        }
        form = BlueprintEditForm(data=data)
        self.assertFalse(form.is_valid())
