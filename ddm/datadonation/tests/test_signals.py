from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from ddm.datadonation.models import DonationInstruction, FileUploader
from ddm.projects.models import DonationProject, ResearchProfile


User = get_user_model()


class TestSignals(TransactionTestCase):
    @classmethod
    def setUp(self):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)

        self.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

        self.file_uploader_a = FileUploader.objects.create(
            project=self.project,
            name='basic file uploader',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
            index=1
        )

        self.file_uploader_b = FileUploader.objects.create(
            project=self.project,
            name='basic file uploader B',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
            index=2
        )

        self.file_uploader_c = FileUploader.objects.create(
            project=self.project,
            name='basic file uploader C',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
            index=3
        )

    def test_post_delete_signal_for_donation_instruction(self):
        DonationInstruction.objects.create(file_uploader=self.file_uploader_a, index=1)
        instruction_b = DonationInstruction.objects.create(file_uploader=self.file_uploader_a, index=2)
        instruction_c_pk = DonationInstruction.objects.create(file_uploader=self.file_uploader_a, index=3).pk
        instruction_b.delete()
        instruction_c = DonationInstruction.objects.get(pk=instruction_c_pk)
        self.assertEqual(instruction_c.index, 2)

    def test_post_delete_signal_for_file_uploader(self):
        file_uploader_c_pk = FileUploader.objects.create(
            project=self.project,
            name='basic file uploader C',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
            index=3
        ).pk
        self.file_uploader_b.delete()
        file_uploader_c = FileUploader.objects.get(pk=file_uploader_c_pk)
        self.assertEqual(file_uploader_c.index, 2)
