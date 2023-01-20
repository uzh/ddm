import cProfile
import inspect
import json
import pandas as pd

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from ddm.models.core import (
    ResearchProfile, DonationProject, FileUploader, DonationBlueprint,
    Participant, DataDonation
)


User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class PerformanceTest(TestCase):
    """ Defines shared test data. """
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

    @staticmethod
    def generate_profiler_table(stats):
        """ Generates a pandas dataframe from cProfiler stats. """

        def filter_row(r):
            """ Keeps row only if the recorded function is part of DDM. """
            if 'code' in str(type(r['func'])):
                source_file = inspect.getsourcefile(r['func'])
                if source_file:
                    if '\\lib\\' in source_file:
                        return False
                    else:
                        return True
            return False

        df = pd.DataFrame(
            stats,
            columns=['func', 'ncalls', 'ccalls', 'tottime', 'inlinetime', 'callers']
        )
        return df[df.apply(lambda x: filter_row(x), axis=1)]

    @staticmethod
    def print_result_to_console(stats, header):
        """
        Print execution time and the 5 functions with the largest inline times.
        """
        print('------------------------------------------------------')
        print(header)
        print(f'  Execution time: {stats["tottime"].max()}')
        print(f'  Top 5 functions with longest execution time:')
        for k, r in stats.nlargest(5, 'inlinetime').iterrows():
            print(f'     Function:    {r["func"]}')
            print(f'     Inline time: {r["inlinetime"]}')
            print(f'     Ncalls:      {r["ncalls"]}; ccalls: {r["ccalls"]}')
        return


class TestDonationBlueprintModel(PerformanceTest):
    def test_blueprint_donation_save_time(self):
        """
        Test execution times to encrypt and save a donation for varying donation sizes.
        """

        # Load test data donation.
        with open('../ddm/tests/files_for_tests/test_data_1mb.json') as file:
            data_1mb = json.load(file)

        # Run execution time tests.
        times = []
        for size in [1, 5, 10, 100]:
            response = {
                'consent': True,
                'extracted_data': json.dumps(data_1mb * size),
                'status': 'some status'
            }

            with cProfile.Profile() as profiler:
                profiler.enable()
                self.blueprint.process_donation(response, self.participant)
                profiler.disable()

                # Get statistics.
                profiler_stats = PerformanceTest.generate_profiler_table(profiler.getstats())

                # Update results list.
                times.append(profiler_stats['tottime'].max())

                # Print test results to console.
                header = f'Results for donation of size {size}mb'
                PerformanceTest.print_result_to_console(profiler_stats, header)

        print(f'\nExecution times: {times}')
        return


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestDownloadAPIPerformance(PerformanceTest):

    def test_api_download_time(self):
        """ Profile blueprint processing performance. """
        with open('../ddm/tests/files_for_tests/test_data_1mb.json') as file:
            data_1mb = json.load(file)

        donation_size = 10
        donation_data = {
            'consent': True,
            'extracted_data': json.dumps(data_1mb*donation_size),
            'status': 'some status'
        }

        self.client.login(**self.user_creds)

        # Run execution time tests.
        times = []
        n_donations = 0
        n_runs = 2
        for i in range(1, n_runs + 1):
            for _ in range(10):
                DataDonation.objects.create(
                    project=self.project,
                    blueprint=self.blueprint,
                    participant=self.participant,
                    consent=donation_data['consent'],
                    status=donation_data['status'],
                    data=donation_data['extracted_data']
                )
            n_donations += 10

            with cProfile.Profile() as profiler:
                header = {'Super-Secret': None}
                profiler.enable()
                self.client.get(reverse('ddm-data-api', args=[self.project.pk]), **header)
                profiler.disable()

                # Get statistics.
                profiler_stats = PerformanceTest.generate_profiler_table(profiler.getstats())

                # Update results list.
                times.append(profiler_stats['tottime'].max())

                # Print test results to console.
                header = f'Results for run {i}/{n_runs} with {n_donations} donations à {donation_size}mb'
                PerformanceTest.print_result_to_console(profiler_stats, header)

        print(f'\nExecution times: {times}')
        return
