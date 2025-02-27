from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ddm.datadonation.models import FileUploader, DonationBlueprint
from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers
from ddm.projects.models import DonationProject, ResearchProfile


User = get_user_model()


class TestExceptionAPI(TestCase):
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

        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name='valid blueprint',
            description='some description',
            expected_fields='"some field"',
            file_uploader=cls.file_uploader,
            regex_path='/this/file.json'
        )

        cls.post_url = reverse('ddm_logging:exceptions_api', args=[cls.project.url_id])
        cls.post_data = {
            'blueprint': cls.blueprint.pk,
            'status_code': 1,
            'raised_by': ExceptionRaisers.SERVER,
            'message': 'Some message.'
        }

    def test_post_without_participant(self):
        client = Client()
        exceptions_count_before = ExceptionLogEntry.objects.count()
        client.post(self.post_url, self.post_data)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))

    def test_valid_post(self):
        client = Client()
        client.get(reverse('ddm_participation:briefing', args=[self.project.slug]))
        exceptions_count_before = ExceptionLogEntry.objects.count()
        client.post(self.post_url, self.post_data)
        exceptions_count_after = ExceptionLogEntry.objects.count()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))
