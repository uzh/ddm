from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, Client
from django.urls import reverse
from django.utils import timezone

from ddm.datadonation.models import DonationBlueprint, FileUploader, DataDonation
from ddm.participation.models import Participant

from ddm.projects.models import ResearchProfile, DonationProject

User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
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

        cls.url = reverse('ddm_datadonation:blueprints:edit',
                          kwargs={'pk': cls.blueprint.pk, 'project_url_id': cls.project.url_id})

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
        redirect_url = reverse(
            'ddm_datadonation:overview',
            kwargs={'project_url_id': self.project.url_id}
        )
        self.assertEqual(response.url, redirect_url)
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


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
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

        cls.url = reverse(
            'ddm_datadonation:uploaders:edit',
            kwargs={'pk': cls.file_uploader.pk, 'project_url_id': cls.project.url_id}
        )

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
        redirect_url = reverse(
            'ddm_datadonation:overview',
            kwargs={'project_url_id': self.project.url_id}
        )
        self.assertEqual(
            response.url,
            redirect_url
        )
        self.assertEqual(
            FileUploader.objects.get(pk=self.file_uploader.pk).name,
            valid_data['name']
        )
        self.assertNotEqual(
            bp_a_uploader_before,
            bp_a_uploader_after
        )
        self.assertNotEqual(
            bp_b_uploader_before,
            bp_b_uploader_after
        )

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
            invalid_data['name']
        )
        self.assertEqual(
            bp_a_uploader_before,
            bp_a_uploader_after
        )
        self.assertEqual(
            bp_b_uploader_before,
            bp_b_uploader_after
        )


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestAPIs(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.base_creds = {
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        }
        base_user = User.objects.create_user(**cls.base_creds)
        base_profile = ResearchProfile.objects.create(
            user=base_user
        )

        cls.no_perm_creds = {
            'username': 'non-perm', 'password': '123', 'email': 'non-perm@mail.com'
        }
        no_perm_user = User.objects.create_user(**cls.no_perm_creds)
        no_perm_profile = ResearchProfile.objects.create(
            user=no_perm_user
        )

        cls.project_base = DonationProject.objects.create(
            name='Base Project',
            slug='base',
            owner=base_profile
        )
        cls.project_alt = DonationProject.objects.create(
            name='Alt Project',
            slug='alternative',
            owner=no_perm_profile
        )
        cls.project_secret = DonationProject.objects.create(
            name='Secret Project',
            slug='super-secret',
            owner=base_profile,
            super_secret=True,
            secret_key='secret_key'
        )

        cls.participant_regular = Participant.objects.create(
            project=cls.project_base,
            start_time=timezone.now()
        )
        cls.participant_secret = Participant.objects.create(
            project=cls.project_secret,
            start_time=timezone.now()
        )

        cls.blueprint_regular = DonationBlueprint.objects.create(
            project=cls.project_base,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=None
        )
        cls.blueprint_secret = DonationBlueprint.objects.create(
            project=cls.project_secret,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=None
        )

        cls.donation_regular = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_regular,
            participant=cls.participant_regular,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data=['data1_pA_bpA', 'data2_pA_bpA']
        )
        cls.donation_secret = DataDonation.objects.create(
            project=cls.project_secret,
            blueprint=cls.blueprint_secret,
            participant=cls.participant_secret,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data=['data1_pA_bpB', 'data2_pA_bpB']
        )

    def test_donation_download_view_valid_login_regular_project(self):
        self.client.login(**self.base_creds)
        url = reverse(
            'ddm_datadonation:download_donation',
            args=[self.project_base.url_id, self.participant_regular.external_id]
        )
        get_response = self.client.get(url, follow=True)
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(url, {})
        self.assertEqual(post_response.status_code, 200)

    def test_donation_download_view_valid_login_secret_project(self):
        self.client.login(**self.base_creds)
        url = reverse(
            'ddm_datadonation:download_donation',
            args=[self.project_secret.url_id, self.participant_secret.external_id]
        )
        get_response = self.client.get(url, follow=True)
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(url, {'secret': 'secret_key'})
        self.assertEqual(post_response.status_code, 200)

        post_response = self.client.post(url, {'secret': 'nonsense'})
        self.assertEqual(post_response.status_code, 422)

    def test_donation_download_view_invalid_login_regular_project(self):
        self.client.login(**self.no_perm_creds)
        url = reverse(
            'ddm_datadonation:download_donation',
            args=[self.project_base.url_id, self.participant_regular.external_id]
        )
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 404)

        post_response = self.client.post(url, {})
        self.assertEqual(post_response.status_code, 404)

    def test_donation_download_view_invalid_login_secret_project(self):
        self.client.login(**self.no_perm_creds)
        url = reverse(
            'ddm_datadonation:download_donation',
            args=[self.project_secret.url_id, self.participant_secret.external_id]
        )
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 404)

        post_response = self.client.post(url, {'secret': 'secret_key'})
        self.assertEqual(post_response.status_code, 404)

    def test_donation_download_view_not_logged_in_regular_project(self):
        client = Client()
        url = reverse(
            'ddm_datadonation:download_donation',
            args=[self.project_base.url_id, self.participant_regular.external_id]
        )
        get_response = client.get(url)
        self.assertRedirects(get_response, reverse('ddm_login'))

        post_response = self.client.post(url, {})
        self.assertRedirects(post_response, reverse('ddm_login'))

    def test_donation_download_view_not_logged_in_secret_project(self):
        client = Client()
        url = reverse(
            'ddm_datadonation:download_donation',
            args=[self.project_secret.url_id, self.participant_secret.external_id]
        )
        get_response = client.get(url)
        self.assertRedirects(get_response, reverse('ddm_login'))

        post_response = self.client.post(url, {'secret': 'secret_key'})
        self.assertRedirects(post_response, reverse('ddm_login'))
