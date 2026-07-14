from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.participation.utils import (
    get_filter_config_id,
    get_filter_source_config_id,
    get_filter_target_config_id,
)
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.constants import FilterSourceTypes
from ddm.questionnaire.models import (
    FilterCondition,
    QuestionItem,
    SingleChoiceQuestion,
)

User = get_user_model()


class FilterUtilsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="utils_owner", password="123", email="utils@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="UtilsProject", slug="utils-proj", owner=profile
        )

        cls.question = SingleChoiceQuestion.objects.create(
            project=cls.project,
            name="Q1",
            variable_name="q1",
            page=1,
            index=1,
        )
        cls.item = QuestionItem.objects.create(
            question=cls.question,
            index=1,
            value=1,
            label="Item",
        )
        cls.question_source = SingleChoiceQuestion.objects.create(
            project=cls.project,
            name="Q2",
            variable_name="q2",
            page=1,
            index=2,
        )
        cls.item_source = QuestionItem.objects.create(
            question=cls.question_source,
            index=1,
            value=1,
            label="Src Item",
        )

    # Tests for get_filter_config_id ------------------------------------------
    def test_get_filter_config_id_for_question(self):
        result = get_filter_config_id(self.question)
        self.assertEqual(result, f"question-{self.question.pk}")

    def test_get_filter_config_id_for_item(self):
        result = get_filter_config_id(self.item)
        self.assertEqual(result, f"item-{self.item.pk}")

    # Tests for get_filter_target_config_id -----------------------------------
    def test_target_config_id_for_question_target(self):
        fc = FilterCondition.objects.create(
            target_question=self.question,
            source_type=FilterSourceTypes.QUESTION,
            source_question=self.question_source,
            index=1,
        )
        self.assertEqual(
            get_filter_target_config_id(fc), f"question-{self.question.pk}"
        )

    def test_target_config_id_for_item_target(self):
        fc = FilterCondition.objects.create(
            target_item=self.item,
            source_type=FilterSourceTypes.QUESTION,
            source_question=self.question_source,
            index=1,
        )
        self.assertEqual(get_filter_target_config_id(fc), f"item-{self.item.pk}")

    def test_target_config_id_raises_for_no_target(self):
        fc = FilterCondition(
            source_type=FilterSourceTypes.QUESTION,
            index=1,
        )
        with self.assertRaises(ValueError):
            get_filter_target_config_id(fc)

    # Tests for get_filter_source_config_id -----------------------------------
    def test_source_config_id_for_question_source(self):
        fc = FilterCondition.objects.create(
            target_question=self.question,
            source_type=FilterSourceTypes.QUESTION,
            source_question=self.question_source,
            index=1,
        )
        self.assertEqual(
            get_filter_source_config_id(fc), f"question-{self.question_source.pk}"
        )

    def test_source_config_id_for_item_source(self):
        fc = FilterCondition.objects.create(
            target_question=self.question,
            source_type=FilterSourceTypes.QUESTION_ITEM,
            source_item=self.item_source,
            index=2,
        )
        self.assertEqual(get_filter_source_config_id(fc), f"item-{self.item_source.pk}")

    def test_source_config_id_for_non_model_source(self):
        fc = FilterCondition.objects.create(
            target_question=self.question,
            source_type=FilterSourceTypes.URL_PARAMETER,
            source_identifier="my_param",
            index=3,
        )
        self.assertEqual(get_filter_source_config_id(fc), "my_param")
