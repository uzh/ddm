from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ddm.datadonation.models import DonationInstruction, FileUploader, DonationBlueprint, DataDonation, ProcessingRule
from ddm.logging.models import ExceptionLogEntry
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile


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

    def test_clean(self):
        instruction_in_db = DonationInstruction.objects.create(
            text='instruction',
            index=20,
            file_uploader=self.file_uploader
        )
        instruction_not_in_db = DonationInstruction(
            text='instruction',
            index=21,
            file_uploader=self.file_uploader
        )
        with self.assertRaises(ValidationError):
            instruction_in_db.clean()
            instruction_not_in_db.clean()


class TestDonationBlueprintModel(TestCase):
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

        cls.blueprint = DonationBlueprint.objects.create(
            project=project,
            name='valid blueprint',
            description='some description',
            expected_fields='"some field"',
            file_uploader=cls.file_uploader,
            regex_path='/this/file.json'
        )

        cls.participant = Participant.objects.create(
            project=project,
            start_time=timezone.now()
        )

        ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name='',
            field='fieldA',
            execution_order=1,
        )

        ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name='',
            field='fieldB',
            execution_order=2,
            comparison_operator=ProcessingRule.ComparisonOperators.EQUAL,
        )

        ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name='',
            field='fieldC',
            execution_order=3,
        )

    def test_get_slug(self):
        self.assertEqual(self.blueprint.get_slug(), 'blueprint')

    def test_validate_donation_case_valid(self):
        data = {
            'consent': True,
            'extracted_data': ['some data'],
            'status': 'success'
        }
        self.assertTrue(self.blueprint.validate_donation(data))

    def test_validate_donation_case_invalid(self):
        data = {
            'consent': True,
            'extracted_data': ['some data'],
        }
        self.assertFalse(self.blueprint.validate_donation(data))

    def test_process_donation_case_valid(self):
        data = {
            'consent': True,
            'extracted_data': ['some data'],
            'status': 'success'
        }
        n_donations_pre = DataDonation.objects.count()
        self.blueprint.process_donation(data, self.participant)
        n_donations_post = DataDonation.objects.count()
        self.assertEqual(n_donations_post - n_donations_pre, 1)

    def test_process_donation_case_invalid(self):
        data = {
            'consent': True,
            'extracted_data': ['some data'],
        }
        n_donations_pre = DataDonation.objects.count()
        n_exceptions_pre = ExceptionLogEntry.objects.count()

        self.blueprint.process_donation(data, self.participant)

        n_donations_post = DataDonation.objects.count()
        n_exceptions_post = ExceptionLogEntry.objects.count()

        self.assertEqual(n_donations_post - n_donations_pre, 0)
        self.assertEqual(n_exceptions_post - n_exceptions_pre, 2)

    def test_get_fields_to_extract(self):
        expected_fields = ['fieldA', 'fieldC']
        self.assertEqual(
            sorted(self.blueprint.get_fields_to_extract()), sorted(expected_fields))


class TestProcessingRuleModel(TestCase):
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

        cls.blueprint = DonationBlueprint.objects.create(
            project=project,
            name='valid blueprint',
            description='some description',
            expected_fields='"some field"',
            file_uploader=cls.file_uploader,
            regex_path='/this/file.json'
        )

        cls.participant = Participant.objects.create(
            project=project,
            start_time=timezone.now()
        )

    def test_get_rule_config(self):
        rule = ProcessingRule.objects.create(
            blueprint=self.blueprint,
            name='test name',
            field='some field',
            execution_order=1,
            comparison_operator=ProcessingRule.ComparisonOperators.EMPTY,
        )
        expected_config = {
            'field': 'some field',
            'regex_field': False,
            'comparison_operator': ProcessingRule.ComparisonOperators.EMPTY,
            'comparison_value': '',
            'replacement_value': ''
        }
        self.assertEqual(rule.get_rule_config(), expected_config)
