from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.participation.utils import get_filter_source_config_id, get_filter_target_config_id
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import (
    SingleChoiceQuestion, QuestionItem, MultiChoiceQuestion, MatrixQuestion,
    ScalePoint, SemanticDifferential, FilterCondition,
    OpenQuestion
)
from ddm.questionnaire.constants import FilterSourceTypes

User = get_user_model()


class TestQuestionModelsBaseCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

        cls.question_config = {
            'project': cls.project,
            'name': 'Test Question',
            'page': 1,
            'index': 1,
            'variable_name': 'test_var',
            'text': 'Question Text',
        }


class TestSingleChoiceQuestion(TestQuestionModelsBaseCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.question = SingleChoiceQuestion.objects.create(**cls.question_config)
        QuestionItem.objects.create(question=cls.question, index=1, value=1)
        QuestionItem.objects.create(question=cls.question, index=2, value=8)

    def test_get_valid_responses(self):
        valid_values = [1, 8, -99, -77]
        self.assertCountEqual(valid_values, self.question.get_valid_responses())


class TestMultiChoiceQuestion(TestQuestionModelsBaseCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.question = MultiChoiceQuestion.objects.create(**cls.question_config)
        cls.item_a = QuestionItem.objects.create(
            question=cls.question, index=1, value=1)
        cls.item_b = QuestionItem.objects.create(
            question=cls.question, index=2, value=8)

    def test_get_valid_responses(self):
        valid_values = [1, 0, -99, -77]
        self.assertCountEqual(valid_values, self.question.get_valid_responses())


class TestMatrixQuestion(TestQuestionModelsBaseCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.question = MatrixQuestion.objects.create(**cls.question_config)
        cls.item_a = QuestionItem.objects.create(
            question=cls.question, index=1, value=1)
        cls.item_b = QuestionItem.objects.create(
            question=cls.question, index=2, value=8)
        cls.scale_a = ScalePoint.objects.create(
            question=cls.question, index=1, value=1)
        cls.scale_b = ScalePoint.objects.create(
            question=cls.question, index=2, value=6)

    def test_get_valid_responses(self):
        valid_values = [1, 6, -99, -77]
        self.assertCountEqual(valid_values, self.question.get_valid_responses())


class TestSemanticDifferentialQuestion(TestQuestionModelsBaseCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.question = SemanticDifferential.objects.create(**cls.question_config)
        cls.item_a = QuestionItem.objects.create(
            question=cls.question, index=1, value=1)
        cls.item_b = QuestionItem.objects.create(
            question=cls.question, index=2, value=8)
        cls.scale_a = ScalePoint.objects.create(
            question=cls.question, index=1, value=1)
        cls.scale_b = ScalePoint.objects.create(
            question=cls.question, index=2, value=6)

    def test_get_valid_responses(self):
        valid_values = [1, 6, -99, -77]
        self.assertCountEqual(valid_values, self.question.get_valid_responses())


class FilterConditionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name='Base Project',
            slug='base',
            owner=profile,
            expected_url_parameters="url-param-a"
        )

        cls.question = OpenQuestion.objects.create(
            project=cls.project,
            name='open question',
            variable_name='open_question'
        )
        cls.question_alt = OpenQuestion.objects.create(
            project=cls.project,
            name='open question 2',
            variable_name='open_question_alt'
        )
        cls.item = QuestionItem.objects.create(
            question=cls.question_alt,
            index=1,
            value=1
        )

        cls.filter_target_question = FilterCondition.objects.create(
            index=1,
            combinator='AND',
            condition_operator='==',
            condition_value='some_value',
            target_question=cls.question,
            source_type=FilterSourceTypes.QUESTION_ITEM,
            source_item=cls.item
        )

        cls.filter_target_item = FilterCondition.objects.create(
            index=1,
            combinator='OR',
            condition_operator='!=',
            condition_value='another_value',
            target_item=cls.item,
            source_type=FilterSourceTypes.QUESTION,
            source_question=cls.question
        )

    def test_get_target_question(self):
        target = self.filter_target_question.get_target()
        self.assertEqual(target, self.question)

    def test_get_target_item(self):
        target = self.filter_target_item.get_target()
        self.assertEqual(target, self.item)

    def test_get_related_project_question(self):
        related_project = self.filter_target_question.get_related_project()
        self.assertEqual(related_project, self.project)

    def test_get_related_project_item(self):
        related_project = self.filter_target_item.get_related_project()
        self.assertEqual(related_project, self.project)

    def test_get_source_question(self):
        source = self.filter_target_item.get_source()
        expected_source = self.question
        self.assertEqual(source, expected_source)

    def test_get_source_item(self):
        source = self.filter_target_question.get_source()
        expected_source = self.item
        self.assertEqual(source, expected_source)

    def test_get_source_url_parameter(self):
        filter_condition = FilterCondition.objects.create(
            index=1,
            combinator='AND',
            condition_operator='==',
            condition_value='some_value',
            target_question=self.question,
            source_type=FilterSourceTypes.URL_PARAMETER,
            source_identifier='_url_url-param-a'
        )
        source = filter_condition.get_source()
        expected_source = filter_condition.source_identifier
        self.assertEqual(source, expected_source)

        filter_condition.source_identifier = 'non_existing_identifier'
        source_non_existent = filter_condition.get_source()
        self.assertIsNone(source_non_existent)

    def test_get_source_system_variable(self):
        filter_condition = FilterCondition.objects.create(
            index=1,
            combinator='AND',
            condition_operator='==',
            condition_value='some_value',
            target_question=self.question,
            source_type=FilterSourceTypes.SYSTEM,
            source_identifier='_url_url-param-a'
        )
        source = filter_condition.get_source()
        expected_source = filter_condition.source_identifier
        self.assertEqual(source, expected_source)

    def test_get_source_participant_variable(self):
        filter_condition = FilterCondition.objects.create(
            index=1,
            combinator='AND',
            condition_operator='==',
            condition_value='some_value',
            target_question=self.question,
            source_type=FilterSourceTypes.PARTICIPANT,
            source_identifier='_participant_id'
        )
        source = filter_condition.get_source()
        expected_source = filter_condition.source_identifier
        self.assertEqual(source, expected_source)

        filter_condition.source_identifier = 'non_existing_identifier'
        source_non_existent = filter_condition.get_source()
        self.assertIsNone(source_non_existent)

    def test_get_source_donation(self):
        filter_condition = FilterCondition.objects.create(
            index=1,
            combinator='AND',
            condition_operator='==',
            condition_value='some_value',
            target_question=self.question,
            source_type=FilterSourceTypes.DONATION,
            source_identifier='_donation_n_success'
        )
        source = filter_condition.get_source()
        expected_source = filter_condition.source_identifier
        self.assertEqual(source, expected_source)

    def test_get_source_config_id_question(self):
        config_id = get_filter_source_config_id(self.filter_target_item)
        expected_id = f'{FilterSourceTypes.QUESTION}-{self.question.pk}'
        self.assertEqual(config_id, expected_id)

    def test_get_source_config_id_item(self):
        config_id = get_filter_source_config_id(self.filter_target_question)
        expected_id = f'{FilterSourceTypes.QUESTION_ITEM}-{self.item.pk}'
        self.assertEqual(config_id, expected_id)

    def test_get_source_config_id_other(self):
        filter_condition = FilterCondition.objects.create(
            index=1,
            combinator='AND',
            condition_operator='==',
            condition_value='some_value',
            target_question=self.question,
            source_type=FilterSourceTypes.SYSTEM,
            source_identifier='some_identifier'
        )

        config_id = get_filter_source_config_id(filter_condition)
        expected_id = filter_condition.source_identifier
        self.assertEqual(config_id, expected_id)

    def test_get_target_config_id_question(self):
        config_id = get_filter_target_config_id(self.filter_target_question)
        expected_id = f'{FilterSourceTypes.QUESTION}-{self.question.pk}'
        self.assertEqual(config_id, expected_id)

    def test_get_target_config_id_item(self):
        config_id = get_filter_target_config_id(self.filter_target_item)
        expected_id = f'{FilterSourceTypes.QUESTION_ITEM}-{self.item.pk}'
        self.assertEqual(config_id, expected_id)
