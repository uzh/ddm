from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ddm.datadonation.models import (
    BlueprintFilePath,
    DataDonation,
    DonationBlueprint,
    FileUploader,
)
from ddm.participation.models import Participant
from ddm.participation.services import (
    QuestionnaireConfigService,
    UploaderConfigService,
)
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.constants import FilterSourceTypes
from ddm.questionnaire.models import (
    FilterCondition,
    OpenQuestion,
    QuestionItem,
    SingleChoiceQuestion,
)

User = get_user_model()


class UploaderConfigServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="svc_owner", password="123", email="svc@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="SvcProject", slug="svc-proj", owner=profile
        )

        cls.uploader = FileUploader.objects.create(
            project=cls.project,
            name="Uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name="BP_",
            display_name="BP",
            expected_fields="",
            file_uploader=cls.uploader,
        )
        cls.file_path = BlueprintFilePath.objects.create(
            blueprint=cls.blueprint,
            path=r"some_path/file\.txt",
            priority=1,
            is_regex=True,
        )
        cls.participant = Participant.objects.create(
            project=cls.project,
            start_time=timezone.now(),
        )

    def test_create_configs_returns_list(self):
        result = UploaderConfigService.create_configs(
            FileUploader.objects.filter(pk=self.uploader.pk),
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_create_configs_with_participant(self):
        result = UploaderConfigService.create_configs(
            FileUploader.objects.filter(pk=self.uploader.pk),
            participant=self.participant,
        )
        self.assertEqual(len(result), 1)

    def test_create_configs_empty_queryset(self):
        result = UploaderConfigService.create_configs(
            FileUploader.objects.none(),
        )
        self.assertEqual(result, [])


class QuestionnaireConfigServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="qsvc_owner", password="123", email="qsvc@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="QSvcProject", slug="qsvc-proj", owner=profile
        )

        cls.participant = Participant.objects.create(
            project=cls.project,
            start_time=timezone.now(),
        )

        # General question (no blueprint).
        cls.general_q = SingleChoiceQuestion.objects.create(
            project=cls.project,
            name="General Q",
            variable_name="gen_q",
            page=1,
            index=1,
            text="General question text",
        )

        # Blueprint-linked question with a matching donation.
        cls.uploader = FileUploader.objects.create(
            project=cls.project,
            name="Uploader_",
            display_name="Uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name="BP_",
            display_name="BP",
            expected_fields="",
            file_uploader=cls.uploader,
        )
        cls.file_path = BlueprintFilePath.objects.create(
            blueprint=cls.blueprint,
            path="some_path/file.txt",
            priority=1,
            is_regex=True,
        )
        cls.blueprint_q = OpenQuestion.objects.create(
            project=cls.project,
            name="BP_Q",
            variable_name="bp_q",
            page=2,
            index=1,
            text="Blueprint question text",
            blueprint=cls.blueprint,
            display="small",
            input_type="text",
            multi_item_response=False,
        )
        cls.donation = DataDonation.objects.create(
            project=cls.project,
            blueprint=cls.blueprint,
            participant=cls.participant,
            time_submitted=timezone.now(),
            consent=True,
            status="success",
            data="some donated data",
        )

        # Blueprint-linked question without a donation (should be skipped).
        cls.blueprint_no_don = DonationBlueprint.objects.create(
            project=cls.project,
            name="BP_No_Don",
            display_name="BP No Don",
            expected_fields="",
            file_uploader=cls.uploader,
        )
        cls.blueprint_q_no_don = OpenQuestion.objects.create(
            project=cls.project,
            name="BP Q No Don",
            variable_name="bp_q_no_don",
            page=3,
            index=1,
            text="No donation",
            blueprint=cls.blueprint_no_don,
            display="small",
            input_type="text",
            multi_item_response=False,
        )

        # Extra objects
        cls.source_q = SingleChoiceQuestion.objects.create(
            project=cls.project,
            name="Src",
            variable_name="src_q",
            page=1,
            index=10,
        )
        cls.source_q_item = QuestionItem.objects.create(
            question=cls.source_q,
            index=1,
            value=1,
            label="A",
        )

    # Tests for create_questionnaire_config -----------------------------------
    def test_create_questionnaire_config_returns_list(self):
        svc = QuestionnaireConfigService(self.project, self.participant)
        result = svc.create_questionnaire_config()
        self.assertIsInstance(result, list)

    def test_general_question_included_in_config(self):
        svc = QuestionnaireConfigService(self.project, self.participant)
        result = svc.create_questionnaire_config()
        question_ids = [q["question"] for q in result]
        self.assertIn(f"question-{self.general_q.pk}", question_ids)

    def test_blueprint_question_with_donation_success_included(self):
        svc = QuestionnaireConfigService(self.project, self.participant)
        result = svc.create_questionnaire_config()
        question_ids = [q["question"] for q in result]
        self.assertIn(f"question-{self.blueprint_q.pk}", question_ids)

    def test_blueprint_question_with_donation_failed_excluded(self):
        svc = QuestionnaireConfigService(self.project, self.participant)
        self.donation.status = "failed"
        self.donation.save()
        result = svc.create_questionnaire_config()
        question_ids = [q["question"] for q in result]
        self.assertNotIn(f"question-{self.blueprint_q.pk}", question_ids)

    def test_blueprint_question_without_donation_excluded(self):
        svc = QuestionnaireConfigService(self.project, self.participant)
        result = svc.create_questionnaire_config()
        question_ids = [q["question"] for q in result]
        self.assertNotIn(f"question-{self.blueprint_q_no_don.pk}", question_ids)

    def test_questions_ordered_by_page_and_index(self):
        svc = QuestionnaireConfigService(self.project, self.participant)
        result = svc.create_questionnaire_config()
        pages = [(q["page"], q["index"]) for q in result]
        self.assertEqual(pages, sorted(pages))

    # Tests for get_filter_config ----------------------------------------------
    def test_get_filter_config_returns_list(self):
        svc = QuestionnaireConfigService(self.project, self.participant)
        result = svc.get_filter_config(self.general_q)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_get_filter_config_resets_first_combinator(self):
        FilterCondition.objects.create(
            target_question=self.general_q,
            source_type=FilterSourceTypes.QUESTION,
            source_question=self.source_q,
            index=1,
            combinator=FilterCondition.ConditionCombinators.AND,
        )
        svc = QuestionnaireConfigService(self.project, self.participant)
        result = svc.get_filter_config(self.general_q)
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["combinator"])

    def test_get_filter_config_return_content(self):
        FilterCondition.objects.create(
            target_question=self.general_q,
            source_type=FilterSourceTypes.QUESTION,
            source_question=self.source_q,
            index=1,
            combinator=FilterCondition.ConditionCombinators.AND,
        )
        FilterCondition.objects.create(
            target_question=self.general_q,
            source_type=FilterSourceTypes.QUESTION_ITEM,
            source_item=self.source_q_item,
            index=2,
            combinator=FilterCondition.ConditionCombinators.OR,
        )

        svc = QuestionnaireConfigService(self.project, self.participant)
        result = svc.get_filter_config(self.general_q)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["index"], 1)
        self.assertEqual(result[1]["index"], 2)

    # Tests for remove_inactive_filters ---------------------------------------
    def test_remove_inactive_filters_excludes_non_existing(self):
        source_q = SingleChoiceQuestion.objects.create(
            project=self.project,
            name="Src2",
            variable_name="src_q2",
            page=1,
            index=11,
        )
        active_fc = FilterCondition.objects.create(
            target_question=self.general_q,
            source_type=FilterSourceTypes.QUESTION,
            source_question=source_q,
            index=10,
            source_exists=True,
        )
        inactive_fc = FilterCondition.objects.create(
            target_question=self.general_q,
            source_type=FilterSourceTypes.URL_PARAMETER,
            source_identifier="nonexistent_param",
            index=11,
            source_exists=True,
        )
        qs = FilterCondition.objects.filter(
            pk__in=[active_fc.pk, inactive_fc.pk],
            source_exists=True,
        ).order_by("index")
        result = QuestionnaireConfigService.remove_inactive_filters(qs)
        result_pks = [fc.pk for fc in result]
        self.assertIn(active_fc.pk, result_pks)
