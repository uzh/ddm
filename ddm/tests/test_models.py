from ddm.models.core import DonationInstruction
from ddm.tests.base import TestData


class TestDonationInstructionModel(TestData):
    def setUp(self):
        self.inst_2 = DonationInstruction.objects.create(
            text='blueprint 2',
            index=2,
            file_uploader=self.file_uploader
        )
        self.inst_3 = DonationInstruction.objects.create(
            text='blueprint 3',
            index=3,
            file_uploader=self.file_uploader
        )

    def test_create_with_existing_index_pushes_other_indices(self):
        new_instruction = DonationInstruction.objects.create(
            text='blueprint new',
            index=2,
            file_uploader=self.file_uploader
        )
        self.assertEqual(new_instruction.index, 2)
        self.assertEqual(DonationInstruction.objects.get(text='blueprint 2', file_uploader=self.file_uploader).index, 3)
        self.assertEqual(DonationInstruction.objects.get(text='blueprint 3', file_uploader=self.file_uploader).index, 4)

    def test_decrease_index_of_existing_instruction(self):
        self.inst_3.index = 2
        self.inst_3.save()
        self.assertEqual(self.inst_3.index, 2)
        self.assertEqual(DonationInstruction.objects.get(text='blueprint 2', file_uploader=self.file_uploader).index, 3)

    def test_increase_index_of_existing_instruction(self):
        self.inst_2.index = 3
        self.inst_2.save()
        self.assertEqual(self.inst_2.index, 3)
        self.assertEqual(DonationInstruction.objects.get(text='blueprint 3', file_uploader=self.file_uploader).index, 2)

    def test_indices_are_adjusted_on_delete(self):
        self.inst_2.delete()
        self.assertEqual(DonationInstruction.objects.get(text='blueprint 3', file_uploader=self.file_uploader).index, 2)
