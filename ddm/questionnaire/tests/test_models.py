from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.exceptions import QuestionValidationError
from ddm.questionnaire.models import (
    SingleChoiceQuestion, QuestionItem, MultiChoiceQuestion, MatrixQuestion,
    ScalePoint, SemanticDifferential
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

    def test_validate_response_valid_case(self):
        valid_values = [1, 8, -99, '1', '8', '-99']
        for value in valid_values:
            self.assertTrue(self.question.validate_response(value))

    def test_validate_response_invalid_case(self):
        invalid_values = [0, 1.4, '4', '1.7', 'abc']
        for value in invalid_values:
            with self.assertRaises(QuestionValidationError):
                self.question.validate_response(value)


class TestMultiChoiceQuestion(TestQuestionModelsBaseCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.question = MultiChoiceQuestion.objects.create(**cls.question_config)
        cls.item_a = QuestionItem.objects.create(
            question=cls.question, index=1, value=1)
        cls.item_b = QuestionItem.objects.create(
            question=cls.question, index=2, value=8)

    def test_validate_response_valid_case(self):
        valid_values = [
            {str(self.item_a.pk): 1, str(self.item_b.pk): 0},
            {self.item_a.pk: False, str(self.item_b.pk): '-99'},
            {self.item_a.pk: True, self.item_b.pk: -99},
        ]
        for value in valid_values:
            self.assertTrue(self.question.validate_response(value))

    def test_validate_response_invalid_case(self):
        invalid_values = [
            {str(self.item_a.pk): 1},
            {self.item_a.pk: 'False', str(self.item_b.pk): 0},
            {self.item_a.pk: 1, self.item_b.pk: 1, '3': 1},
        ]
        for value in invalid_values:
            with self.assertRaises(QuestionValidationError):
                self.question.validate_response(value)


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

    def test_validate_response_valid_case(self):
        valid_values = [
            {str(self.item_a.pk): 1, str(self.item_b.pk): 6},
            {self.item_a.pk: '1', str(self.item_b.pk): '-99'},
            {self.item_a.pk: '6', self.item_b.pk: -99},
        ]
        for value in valid_values:
            self.assertTrue(self.question.validate_response(value))

    def test_validate_response_invalid_case(self):
        invalid_values = [
            {str(self.item_a.pk): 1},
            {self.item_a.pk: 1, str(self.item_b.pk): 0},
            {self.item_a.pk: 1, self.item_b.pk: 1, '3': 1},
        ]
        for value in invalid_values:
            with self.assertRaises(QuestionValidationError):
                self.question.validate_response(value)


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

    def test_validate_response_valid_case(self):
        valid_values = [
            {str(self.item_a.pk): 1, str(self.item_b.pk): 6},
            {self.item_a.pk: '1', str(self.item_b.pk): '-99'},
            {self.item_a.pk: '6', self.item_b.pk: -99},
        ]
        for value in valid_values:
            self.assertTrue(self.question.validate_response(value))

    def test_validate_response_invalid_case(self):
        invalid_values = [
            {str(self.item_a.pk): 1},
            {self.item_a.pk: 1, str(self.item_b.pk): 0},
            {self.item_a.pk: 1, self.item_b.pk: 1, '3': 1},
        ]
        for value in invalid_values:
            with self.assertRaises(QuestionValidationError):
                self.question.validate_response(value)

    def test_create_config(self):
        expected_item_config = []
        for item in [self.item_a, self.item_b]:
            expected_item_config.append({
                'id': item.pk,
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
                'label': scale_point.label,
                'index': scale_point.index,
                'value': scale_point.value,
                'add_border': scale_point.add_border,
            })
        expected_config = {
            'question': self.question.pk,
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
