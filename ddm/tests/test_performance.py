import cProfile
import json
import pandas as pd

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from ddm.models.core import (
    ResearchProfile, DonationProject, FileUploader, DonationBlueprint,
    Participant
)


User = get_user_model()


class TestDonationBlueprintModel(TestCase):
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
            name='basic file uploader',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name='donation blueprint',
            expected_fields='"title", "titleUrl"',
            file_uploader=None
        )
        cls.participant = Participant.objects.create(
            project=cls.project,
            start_time=timezone.now()
        )

    def test_blueprint_processing_time(self):
        """ Profile blueprint processing performance. """
        with open('../ddm/tests/files_for_tests/test_data_1mb.json') as file:
            data_1mb = json.load(file)
            data_1mb = json.loads(data_1mb)

        test_results = {
            '1': [],
            '5': [],
            '10': [],
            '100': [],
        }
        test_sizes = [1, 5, 10, 100]
        for test_size in test_sizes:
            response = {
                'consent': True,
                'extracted_data': json.dumps(data_1mb * test_size),
                'status': 'some status'
            }

            for sim in range(10):
                with cProfile.Profile() as profiler:
                    profiler.enable()
                    self.blueprint.process_donation(response, self.participant)
                    profiler.disable()

                s = pd.DataFrame(
                    profiler.getstats(),
                    columns=['func', 'ncalls', 'ccalls', 'tottime', 'inlinetime', 'callers']
                )

                print(f'---- Performance results for {test_size}mb data ------')
                for i, r in s.nlargest(5, 'inlinetime').iterrows():
                    print(f'Func: {r["func"]}\ntime: {r["inlinetime"]}')
                print(f'Total execution time: {s["tottime"].max()}\n----------')

                test_results[str(test_size)].append(s['tottime'].max())

        print(test_results)
        for k, result in test_results.items():
            print(result)
            assert max(result) < 1.0


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestDownloadAPIPerformance(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_creds = {
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        }
        user = User.objects.create_user(**cls.user_creds)
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)
        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name='basic file uploader',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name='donation blueprint',
            expected_fields='"title", "titleUrl"',
            file_uploader=None
        )
        cls.participant = Participant.objects.create(
            project=cls.project,
            start_time=timezone.now()
        )

    def test_api_download_time(self):
        """ Profile blueprint processing performance. """
        with open('../ddm/tests/files_for_tests/test_data_1mb.json') as file:
            data_1mb = json.load(file)
            data_1mb = json.loads(data_1mb)

        donation_data = {
            'consent': True,
            'extracted_data': json.dumps(data_1mb * 10),
            'status': 'some status'
        }
        self.client.login(**self.user_creds)

        times = []
        for i in range(2):
            self.blueprint.create_donation(donation_data, self.participant)

            with cProfile.Profile() as profiler:
                profiler.enable()
                response = self.client.get(
                    reverse('ddm-data-api', args=[self.project.pk]))
                profiler.disable()

                print(response)

                s = pd.DataFrame(
                    profiler.getstats(),
                    columns=['func', 'ncalls', 'ccalls', 'tottime', 'inlinetime', 'callers']
                )

                for k, r in s.nlargest(5, 'inlinetime').iterrows():
                    print(f'Func: {r["func"]}\ntime: {r["inlinetime"]}')
                print(f'Total execution time: {s["tottime"].max()}\n----------')

                times.append(s['tottime'].max())

        print(times)
        assert max(times) < 1.0
