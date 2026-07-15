from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ddm.logging.models import ExceptionLogEntry
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import (
    QuestionItem,
    QuestionnaireResponse,
    SingleChoiceQuestion,
)
from ddm.questionnaire.services import save_questionnaire_response_to_db

User = get_user_model()


class TestQuestionnaireServices(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )

        cls.participant = Participant.objects.create(
            project=cls.project, start_time=timezone.now()
        )

        cls.question_config = {
            "project": cls.project,
            "name": "Test Question",
            "page": 1,
            "index": 1,
            "variable_name": "test_var",
            "text": "Question Text",
        }

        cls.question = SingleChoiceQuestion.objects.create(**cls.question_config)
        cls.item_a = QuestionItem.objects.create(
            question=cls.question, index=1, value=1
        )
        cls.item_b = QuestionItem.objects.create(
            question=cls.question, index=2, value=8
        )

    def test_save_questionnaire_to_db_valid(self):
        valid_responses = {f"question-{self.question.pk}": 1}

        n_responses_before = QuestionnaireResponse.objects.count()
        n_logs_before = ExceptionLogEntry.objects.count()

        save_questionnaire_response_to_db(
            valid_responses, self.project, self.participant
        )

        n_responses_after = QuestionnaireResponse.objects.count()
        n_logs_after = ExceptionLogEntry.objects.count()

        self.assertEqual(n_responses_before + 1, n_responses_after)
        self.assertEqual(n_logs_before, n_logs_after)

    def test_save_questionnaire_to_db_invalid_id(self):
        invalid_responses = {"1": 1, f"question-{self.question.pk}": 1}
        n_responses_before = QuestionnaireResponse.objects.count()
        n_logs_before = ExceptionLogEntry.objects.count()

        save_questionnaire_response_to_db(
            invalid_responses, self.project, self.participant
        )

        n_responses_after = QuestionnaireResponse.objects.count()
        n_logs_after = ExceptionLogEntry.objects.count()

        self.assertEqual(n_responses_before + 1, n_responses_after)
        self.assertEqual(n_logs_before + 1, n_logs_after)

    def test_save_questionnaire_to_db_invalid_response(self):
        valid_responses = {f"question-{self.question.pk}": 5}
        n_responses_before = QuestionnaireResponse.objects.count()
        n_logs_before = ExceptionLogEntry.objects.count()

        save_questionnaire_response_to_db(
            valid_responses, self.project, self.participant
        )

        n_responses_after = QuestionnaireResponse.objects.count()
        n_logs_after = ExceptionLogEntry.objects.count()

        self.assertEqual(n_responses_before + 1, n_responses_after)
        self.assertEqual(n_logs_before + 1, n_logs_after)
