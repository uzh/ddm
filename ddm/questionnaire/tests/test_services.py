from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from ddm.logging.models import ExceptionLogEntry
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import (
    FilterCondition,
    MatrixQuestion,
    QuestionBase,
    QuestionItem,
    QuestionnaireResponse,
    ScalePoint,
    SingleChoiceQuestion,
)
from ddm.questionnaire.services import copy_question, save_questionnaire_response_to_db

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

    def test_is_complete_defaults_true(self):
        responses = {f"question-{self.question.pk}": 1}
        save_questionnaire_response_to_db(responses, self.project, self.participant)
        response = QuestionnaireResponse.objects.get(
            project=self.project, participant=self.participant
        )
        self.assertTrue(response.is_complete)

    def test_repeated_save_for_same_participant_updates_same_row(self):
        responses = {f"question-{self.question.pk}": 1}

        save_questionnaire_response_to_db(responses, self.project, self.participant)
        save_questionnaire_response_to_db(responses, self.project, self.participant)

        self.assertEqual(
            QuestionnaireResponse.objects.filter(
                project=self.project, participant=self.participant
            ).count(),
            1,
        )

    def test_partial_save_then_final_submission_updates_same_row(self):
        responses = {f"question-{self.question.pk}": 1}

        save_questionnaire_response_to_db(
            responses, self.project, self.participant, is_complete=False
        )
        partial = QuestionnaireResponse.objects.get(
            project=self.project, participant=self.participant
        )
        self.assertFalse(partial.is_complete)

        save_questionnaire_response_to_db(
            responses, self.project, self.participant, is_complete=True
        )

        self.assertEqual(
            QuestionnaireResponse.objects.filter(
                project=self.project, participant=self.participant
            ).count(),
            1,
        )
        final = QuestionnaireResponse.objects.get(
            project=self.project, participant=self.participant
        )
        self.assertTrue(final.is_complete)
        self.assertEqual(final.pk, partial.pk)


class TestCopyQuestion(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base-project", owner=profile
        )
        cls.other_project = DonationProject.objects.create(
            name="Other Project", slug="other-project", owner=profile
        )

        cls.question = QuestionBase.objects.create(
            project=cls.project,
            name="test question",
            variable_name="income",
            page=1,
            index=1,
        )
        cls.item_a = QuestionItem.objects.create(
            question=cls.question,
            index=1,
            value=1,
        )
        cls.item_b = QuestionItem.objects.create(
            question=cls.question,
            index=2,
            value=2,
        )
        cls.scale_point = ScalePoint.objects.create(
            question=cls.question,
            index=1,
            input_label="Agree",
            value=1,
        )
        cls.question_filter = FilterCondition.objects.create(
            target_question=cls.question,
            source_item=cls.item_a,
            source_type="item",
            index=1,
        )
        cls.item_filter = FilterCondition.objects.create(
            target_item=cls.item_b,
            source_question=cls.question,
            source_type="question",
            index=1,
        )

    def test_creates_distinct_question_with_suffixed_name(self):
        new_q = copy_question(self.question)
        self.assertNotEqual(new_q.pk, self.question.pk)
        self.assertEqual(new_q.variable_name, "income_copy")
        self.assertEqual(new_q.project, self.question.project)

    def test_original_question_untouched(self):
        copy_question(self.question)
        self.question.refresh_from_db()
        self.assertEqual(self.question.variable_name, "income")
        self.assertEqual(self.question.questionitem_set.count(), 2)

    def test_repeated_copy_increments_suffix(self):
        copy_question(self.question)
        second = copy_question(self.question)
        self.assertEqual(second.variable_name, "income_copy_1")

    def test_same_variable_name_allowed_in_different_project(self):
        _ = QuestionBase.objects.create(
            project=self.other_project,
            name="unrelated question",
            variable_name="income",
            page=1,
            index=1,
        )
        new_q = copy_question(self.question)
        self.assertEqual(new_q.variable_name, "income_copy")
        self.assertTrue(
            QuestionBase.objects.filter(
                project=self.other_project, variable_name="income"
            ).exists()
        )

    def test_copying_into_same_project_does_not_collide_with_other_project(self):
        QuestionBase.objects.create(
            project=self.other_project,
            name="unrelated",
            variable_name="income_copy",  # same target name, different project
            page=1,
            index=1,
        )
        # Should not be forced to "income_copy" just because a question
        # with that name exists in a *different* project.
        new_q = copy_question(self.question)
        self.assertEqual(new_q.variable_name, "income_copy")

    def test_copies_items_and_relinks_to_new_question(self):
        new_q = copy_question(self.question)
        self.assertEqual(new_q.questionitem_set.count(), 2)
        copied_indexes = set(new_q.questionitem_set.values_list("index", flat=True))
        self.assertEqual(copied_indexes, {1, 2})
        self.assertFalse(new_q.questionitem_set.filter(pk=self.item_a.pk).exists())

    def test_copies_scale_points_and_relinks_to_new_question(self):
        new_q = copy_question(self.question)
        self.assertEqual(new_q.scalepoint_set.count(), 1)
        copied_sp = new_q.scalepoint_set.first()
        self.assertEqual(copied_sp.input_label, "Agree")
        self.assertNotEqual(copied_sp.pk, self.scale_point.pk)

    def test_question_filter_condition_relinked_target_but_source_preserved(self):
        new_q = copy_question(self.question)
        new_filter = FilterCondition.objects.get(target_question=new_q)
        self.assertEqual(new_filter.target_question, new_q)
        # source must still point at the ORIGINAL item, per spec
        self.assertEqual(new_filter.source_item, self.item_a)
        self.assertNotEqual(new_filter.pk, self.question_filter.pk)

    def test_item_filter_condition_relinked_target_but_source_preserved(self):
        new_q = copy_question(self.question)
        new_item_b = new_q.questionitem_set.get(index=2)
        new_filter = FilterCondition.objects.get(target_item=new_item_b)
        self.assertEqual(new_filter.target_item, new_item_b)
        # source must still point at the ORIGINAL question, per spec
        self.assertEqual(new_filter.source_question, self.question)
        self.assertNotEqual(new_filter.pk, self.item_filter.pk)

    def test_no_extra_filter_conditions_created(self):
        copy_question(self.question)
        self.assertEqual(FilterCondition.objects.count(), 4)

    def test_rolls_back_completely_on_integrity_error(self):
        # Force a collision partway through by pre-creating a QuestionItem
        # under a to-be-generated pk situation, OR mock save() on the Nth
        # call.
        q_count_before = QuestionBase.objects.count()
        item_count_before = QuestionItem.objects.count()
        fc_count_before = FilterCondition.objects.count()

        with (
            patch.object(
                ScalePoint, "save", side_effect=IntegrityError("forced failure")
            ),
            self.assertRaises(IntegrityError),
        ):
            copy_question(self.question)

        # transaction.atomic should have rolled back the new question,
        # items, and everything else created before the failure point.
        self.assertEqual(QuestionBase.objects.count(), q_count_before)
        self.assertEqual(QuestionItem.objects.count(), item_count_before)
        self.assertEqual(FilterCondition.objects.count(), fc_count_before)

    def test_copies_polymorphic_subclass_correctly(self):
        matrix_q = MatrixQuestion.objects.create(
            project=self.project,
            name="matrix question",
            variable_name="satisfaction",
            page=1,
            index=1,
        )
        new_q = copy_question(matrix_q)

        self.assertIsInstance(new_q, MatrixQuestion)
        self.assertNotEqual(new_q.pk, matrix_q.pk)
        self.assertNotEqual(new_q.id, matrix_q.id)

        # confirm the ORIGINAL wasn't silently mutated by a stray UPDATE
        matrix_q.refresh_from_db()
        self.assertEqual(matrix_q.variable_name, "satisfaction")
