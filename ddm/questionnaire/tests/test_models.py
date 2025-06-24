from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import (
    SingleChoiceQuestion, QuestionItem, MultiChoiceQuestion, MatrixQuestion,
    ScalePoint, SemanticDifferential, QuestionBase, FilterCondition,
    OpenQuestion, get_filter_config_id, FilterSourceTypes
)

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
        valid_values = [1, 8, -99]
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
        valid_values = [1, 0, -99]
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
        valid_values = [1, 6, -99]
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
        valid_values = [1, 6, -99]
        self.assertCountEqual(valid_values, self.question.get_valid_responses())

    def test_create_config(self):
        expected_item_config = []
        for item in [self.item_a, self.item_b]:
            expected_item_config.append({
                'id': f'item-{item.pk}',
                'label': item.label,
                'label_alt': item.label_alt,
                'index': item.index,
                'value': item.value,
                'randomize': item.randomize,
            })
        expected_scale_config = []
        for scale_point in [self.scale_a, self.scale_b]:
            expected_scale_config.append({
                'id': scale_point.pk,
                'input_label': scale_point.input_label,
                'heading_label': scale_point.heading_label,
                'index': scale_point.index,
                'value': scale_point.value,
                'secondary_point': scale_point.secondary_point,
            })
        expected_config = {
            'question': f'question-{self.question.pk}',
            'type': self.question.question_type,
            'page': self.question.page,
            'index': self.question.index,
            'text': self.question.text,
            'required': self.question.required,
            'items': expected_item_config,
            'scale': expected_scale_config,
            'options': {}
        }
        self.assertDictEqual(expected_config, self.question.create_config())


class FilterConditionUtilsTest(TestCase):
    def test_get_filter_config_id_questionitem(self):
        """Test if QuestionItem returns 'item-{id}'."""
        obj = QuestionItem(pk=5)
        result = get_filter_config_id(obj)
        self.assertEqual(result, 'item-5')

    def test_get_filter_config_id_questionbase(self):
        """Test if QuestionBase returns 'question-{id}'."""
        obj = QuestionBase(pk=10)
        result = get_filter_config_id(obj)
        self.assertEqual(result, 'question-10')


class GetFilterConfigTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)

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

        cls.filter_condition_1 = FilterCondition.objects.create(
            index=1,
            combinator='AND',
            condition_operator='==',
            condition_value='some_value',
            target_question=cls.question,
            source_type=FilterSourceTypes.QUESTION_ITEM,
            source_item=cls.item
        )

        cls.filter_condition_2 = FilterCondition.objects.create(
            index=2,
            combinator='OR',
            condition_operator='!=',
            condition_value='another_value',
            target_question=cls.question,
            source_type=FilterSourceTypes.QUESTION_ITEM,
            source_item=cls.item
        )

        cls.filter_condition_alt = FilterCondition.objects.create(
            index=1,
            combinator='OR',
            condition_operator='!=',
            condition_value='another_value',
            target_item=cls.item,
            source_type=FilterSourceTypes.QUESTION,
            source_question=cls.question
        )

    def test_filter_config_list_length(self):
        """Ensure that filter conditions are returned as a list."""
        result = self.question.get_filter_config()
        self.assertEqual(len(result), 2)

    def test_filter_config_order(self):
        """Ensure filter conditions are ordered by index."""
        result = self.question.get_filter_config()
        self.assertEqual(result[0]['index'], 1)
        self.assertEqual(result[1]['index'], 2)

    def test_first_condition_combinator_is_none(self):
        """Ensure the first condition has combinator set to None."""
        result = self.question.get_filter_config()
        self.assertIsNone(result[0]['combinator'])

    def test_filter_config_correct_target_and_source_question(self):
        """Ensure target and source are correctly formatted."""
        result = self.question.get_filter_config()
        self.assertEqual(result[0]['target'], f'question-{self.question.pk}')
        self.assertEqual(result[0]['source'], f'item-{self.filter_condition_1.source_item.pk}')

    def test_filter_config_correct_target_and_source_item(self):
        """Ensure target and source are correctly formatted."""
        result = self.item.get_filter_config()
        self.assertEqual(result[0]['target'], f'item-{self.item.pk}')
        self.assertEqual(result[0]['source'], f'question-{self.question.pk}')
