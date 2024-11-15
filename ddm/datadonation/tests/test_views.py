from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from ddm.datadonation.models import DonationBlueprint, FileUploader

from ddm.projects.models import ResearchProfile, DonationProject


User = get_user_model()


class BlueprintEditTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=cls.user)

        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name='basic file uploader',
            upload_type=FileUploader.UploadTypes.ZIP_FILE
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name='valid blueprint',
            description='some description',
            expected_fields='"some field"',
            file_uploader=cls.file_uploader,
            regex_path='/this/file.json'
        )

        cls.url = reverse('datadonation:blueprints:edit',
                          kwargs={'pk': cls.blueprint.pk, 'project_pk': cls.project.pk})

    def test_post_valid_data(self):
        valid_data = {
            'name': 'some name',
            'description': 'some description',
            'regex_path': '/file.path',
            'exp_file_format': DonationBlueprint.FileFormats.JSON_FORMAT,
            'csv_delimiter': '',
            'file_uploader': self.file_uploader.pk,
            'json_extraction_root': '',
            'expected_fields': '"fieldA"',
            'expected_fields_regex_matching': 'asdflkjklsadjf',
        }
        formset_data = {
            'processingrule_set-TOTAL_FORMS': '1',
            'processingrule_set-INITIAL_FORMS': '0',
        }
        data = {**valid_data, **formset_data}
        bp_name_before = self.blueprint.name
        self.client.login(**{'username': 'owner', 'password': '123'})
        response = self.client.post(self.url, data)
        bp_name_after = DonationBlueprint.objects.get(pk=self.blueprint.pk).name

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('datadonation:overview', kwargs={'project_pk': self.project.pk}))
        self.assertNotEqual(bp_name_before, bp_name_after)

    def test_post_invalid_data(self):
        invalid_data = {
            'name': 'some other name',
            'description': 'some other description',
            'regex_path': '',
            'exp_file_format': DonationBlueprint.FileFormats.JSON_FORMAT,
            'csv_delimiter': '1234567891011'
        }
        formset_data = {
            'processingrule_set-TOTAL_FORMS': '0',
        }
        data = {**invalid_data, **formset_data}
        bp_name_before = self.blueprint.name

        self.client.login(**{'username': 'owner', 'password': '123'})
        response = self.client.post(self.url, data)
        bp_name_after = DonationBlueprint.objects.get(pk=self.blueprint.pk).name

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(bp_name_before, bp_name_after)


class FileUploaderEditTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=cls.user)

        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name='basic file uploader',
            upload_type=FileUploader.UploadTypes.ZIP_FILE
        )

        cls.blueprint_a = DonationBlueprint.objects.create(
            project=cls.project,
            name='valid blueprint',
            description='some description',
            expected_fields='"some field"',
            file_uploader=cls.file_uploader,
            regex_path='/this/file.json'
        )
        cls.blueprint_b = DonationBlueprint.objects.create(
            project=cls.project,
            name='valid blueprint',
            description='some description',
            expected_fields='"some field"',
            file_uploader=None,
            regex_path='/this/file.json'
        )

        cls.url = reverse('datadonation:uploaders:edit',
                          kwargs={'pk': cls.file_uploader.pk, 'project_pk': cls.project.pk})

    def test_post_valid_data(self):
        valid_data = {
            'name': 'some name',
            'index': 1,
            'upload_type': FileUploader.UploadTypes.ZIP_FILE,
            'combined_consent': False,
            f'bp-{self.blueprint_b.pk}': True
        }
        bp_a_uploader_before = DonationBlueprint.objects.get(pk=self.blueprint_a.pk).file_uploader
        bp_b_uploader_before = DonationBlueprint.objects.get(pk=self.blueprint_b.pk).file_uploader
        self.client.login(**{'username': 'owner', 'password': '123'})
        response = self.client.post(self.url, valid_data)
        bp_a_uploader_after = DonationBlueprint.objects.get(pk=self.blueprint_a.pk).file_uploader
        bp_b_uploader_after = DonationBlueprint.objects.get(pk=self.blueprint_b.pk).file_uploader

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('datadonation:overview', kwargs={'project_pk': self.project.pk}))
        self.assertEqual(FileUploader.objects.get(pk=self.file_uploader.pk).name, valid_data['name'])
        self.assertNotEqual(bp_a_uploader_before, bp_a_uploader_after)
        self.assertNotEqual(bp_b_uploader_before, bp_b_uploader_after)

    def test_post_invalid_data(self):
        invalid_data = {
            'name': 'some other name',
            'upload_type': FileUploader.UploadTypes.ZIP_FILE,
            'combined_consent': False
        }
        bp_a_uploader_before = DonationBlueprint.objects.get(pk=self.blueprint_a.pk).file_uploader
        bp_b_uploader_before = DonationBlueprint.objects.get(pk=self.blueprint_b.pk).file_uploader
        self.client.login(**{'username': 'owner', 'password': '123'})
        response = self.client.post(self.url, invalid_data)
        bp_a_uploader_after = DonationBlueprint.objects.get(pk=self.blueprint_a.pk).file_uploader
        bp_b_uploader_after = DonationBlueprint.objects.get(pk=self.blueprint_b.pk).file_uploader

        # Check that the response renders the form with errors (form submission unsuccessful)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertNotEqual(
            FileUploader.objects.get(pk=self.file_uploader.pk).name,
            invalid_data['name'])
        self.assertEqual(bp_a_uploader_before, bp_a_uploader_after)
        self.assertEqual(bp_b_uploader_before, bp_b_uploader_after)
