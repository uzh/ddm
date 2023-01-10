from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.models.core import (
    DonationInstruction, ResearchProfile, DonationProject, FileUploader
)


User = get_user_model()


class TestDonationInstructionModel(TestCase):
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
            name='basic file uploader',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE
        )

    def setUp(self):
        self.inst_2 = DonationInstruction.objects.create(
            text='instruction 2',
            index=2,
            file_uploader=self.file_uploader
        )
        self.inst_3 = DonationInstruction.objects.create(
            text='instruction 3',
            index=3,
            file_uploader=self.file_uploader
        )

    def test_create_with_existing_index_pushes_other_indices(self):
        new_instruction = DonationInstruction.objects.create(
            text='instruction new',
            index=2,
            file_uploader=self.file_uploader
        )
        self.assertEqual(new_instruction.index, 2)

        self.inst_2.refresh_from_db()
        self.assertEqual(self.inst_2.index, 3)

        self.inst_3.refresh_from_db()
        self.assertEqual(self.inst_3.index, 4)

    def test_decrease_index_of_existing_instruction(self):
        self.inst_3.index = 2
        self.inst_3.save()
        self.assertEqual(self.inst_3.index, 2)

        self.inst_2.refresh_from_db()
        self.assertEqual(self.inst_2.index, 3)

    def test_increase_index_of_existing_instruction(self):
        self.inst_2.index = 3
        self.inst_2.save()
        self.assertEqual(self.inst_2.index, 3)

        self.inst_3.refresh_from_db()
        self.assertEqual(self.inst_3.index, 2)

    def test_indices_are_adjusted_on_delete(self):
        self.inst_2.delete()

        self.inst_3.refresh_from_db()
        self.assertEqual(self.inst_3.index, 2)
