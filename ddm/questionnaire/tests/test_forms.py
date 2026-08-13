from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.constants import FilterSourceTypes
from ddm.questionnaire.forms import FilterConditionForm, get_question_form
from ddm.questionnaire.models import (
    FilterCondition,
    MultiChoiceQuestion,
    OpenQuestion,
    QuestionItem,
    SingleChoiceQuestion,
)

User = get_user_model()


class TestOpenQuestionFormMinMaxValidation(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )
        cls.form_class = get_question_form("open")

    def base_data(self, **overrides):
        data = {
            "name": "Test Question",
            "variable_name": "test_var",
            "page": 1,
            "index": 1,
            "text": "Question Text",
            "requirement_level": OpenQuestion.RequirementLevel.NOT_REQUIRED,
            "input_type": "text",
            "min_input_length": "",
            "max_input_length": "",
            "min_number_value": "",
            "max_number_value": "",
            "display": "small",
        }
        data.update(overrides)
        return data

    def test_form_includes_min_max_fields(self):
        form = self.form_class(instance=OpenQuestion(project=self.project))
        for field in (
            "min_input_length",
            "max_input_length",
            "min_number_value",
            "max_number_value",
        ):
            self.assertIn(field, form.fields)

    def test_min_input_length_greater_than_max_is_invalid(self):
        data = self.base_data(min_input_length=10, max_input_length=5)
        form = self.form_class(data=data, instance=OpenQuestion(project=self.project))
        self.assertFalse(form.is_valid())
        self.assertIn("min_input_length", form.errors)
        self.assertIn("max_input_length", form.errors)

    def test_min_number_value_greater_than_max_is_invalid(self):
        data = self.base_data(
            input_type="numbers", min_number_value=10, max_number_value=5
        )
        form = self.form_class(data=data, instance=OpenQuestion(project=self.project))
        self.assertFalse(form.is_valid())
        self.assertIn("min_number_value", form.errors)
        self.assertIn("max_number_value", form.errors)

    def test_valid_bounds_pass(self):
        data = self.base_data(min_input_length=5, max_input_length=10)
        form = self.form_class(data=data, instance=OpenQuestion(project=self.project))
        self.assertTrue(form.is_valid(), form.errors)

    def test_empty_bounds_pass(self):
        data = self.base_data()
        form = self.form_class(data=data, instance=OpenQuestion(project=self.project))
        self.assertTrue(form.is_valid(), form.errors)


class FilterConditionFormChoicesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )
        cls.target_question = OpenQuestion.objects.create(
            project=cls.project, name="open question", variable_name="open_question"
        )

    def test_excludes_target_question_from_source_choices(self):
        """A question can't be filtered against itself."""
        form = FilterConditionForm(
            project=self.project, target_object=self.target_question
        )
        values = [v for v, _ in form.fields["source"].choices]
        self.assertNotIn(
            f"{FilterSourceTypes.QUESTION}-{self.target_question.id}", values
        )

    def test_excludes_single_choice_items_from_item_sources(self):
        other_question = SingleChoiceQuestion.objects.create(
            project=self.project,
            name="sc question",
            variable_name="sc_question",
        )
        item = QuestionItem.objects.create(question=other_question, index=1, value=1)

        form = FilterConditionForm(
            project=self.project, target_object=self.target_question
        )
        values = [v for v, _ in form.fields["source"].choices]
        self.assertNotIn(f"{FilterSourceTypes.QUESTION_ITEM}-{item.id}", values)

    def test_excludes_items_belonging_to_same_question_as_target(self):
        other_question = SingleChoiceQuestion.objects.create(
            project=self.project,
            name="sc question",
            variable_name="sc_question",
        )
        item = QuestionItem.objects.create(question=other_question, index=1, value=1)
        item_2 = QuestionItem.objects.create(question=other_question, index=2, value=2)
        form = FilterConditionForm(project=self.project, target_object=item)
        values = [v for v, _ in form.fields["source"].choices]
        self.assertNotIn(f"{FilterSourceTypes.QUESTION_ITEM}-{item.id}", values)
        self.assertNotIn(f"{FilterSourceTypes.QUESTION_ITEM}-{item_2.id}", values)

    def test_excludes_generic_and_multi_choice_question_types(self):
        excluded = MultiChoiceQuestion.objects.create(
            project=self.project,
            name="mc question",
            variable_name="mc_question",
        )
        form = FilterConditionForm(
            project=self.project, target_object=self.target_question
        )
        values = [v for v, _ in form.fields["source"].choices]
        self.assertNotIn(f"{FilterSourceTypes.QUESTION}-{excluded.id}", values)

    def test_excludes_open_questions_with_multi_item_response(self):
        oq = OpenQuestion.objects.create(
            project=self.project,
            name="open question",
            variable_name="oq",
            multi_item_response=True,
        )
        form = FilterConditionForm(
            project=self.project, target_object=self.target_question
        )
        values = [v for v, _ in form.fields["source"].choices]
        self.assertNotIn(f"{FilterSourceTypes.QUESTION}-{oq.id}", values)


class FilterConditionFormValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )
        cls.target_question = OpenQuestion.objects.create(
            project=cls.project, name="target question", variable_name="tgt_question"
        )
        cls.source_question = OpenQuestion.objects.create(
            project=cls.project, name="source question", variable_name="src_question"
        )

    def _base_data(self, source):
        return {
            "index": 0,
            "combinator": FilterCondition.ConditionCombinators.AND,
            "source": source,
            "condition_operator": FilterCondition.ConditionOperators.EQUALS,
            "condition_value": "x",
        }

    def test_missing_source_is_invalid(self):
        form = FilterConditionForm(
            data=self._base_data(""),
            project=self.project,
            target_object=self.target_question,
        )
        self.assertFalse(form.is_valid())

    def test_malformed_source_is_invalid(self):
        form = FilterConditionForm(
            data=self._base_data("not-a-valid-pair-extra-dash-missing"),
            project=self.project,
            target_object=self.target_question,
        )
        # e.g. a value with no "-" at all
        form.data = form.data.copy()
        form.data["source"] = "nodash"
        self.assertFalse(form.is_valid())

    def test_source_referencing_nonexistent_question_is_invalid(self):
        form = FilterConditionForm(
            data=self._base_data(f"{FilterSourceTypes.QUESTION}-999999"),
            project=self.project,
            target_object=self.target_question,
        )
        self.assertFalse(form.is_valid())

    def test_valid_question_source_passes_validation(self):
        form = FilterConditionForm(
            data=self._base_data(
                f"{FilterSourceTypes.QUESTION}-{self.source_question.id}"
            ),
            project=self.project,
            target_object=self.target_question,
        )
        self.assertTrue(form.is_valid(), form.errors)


class FilterConditionFormSaveTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )
        cls.target_question = OpenQuestion.objects.create(
            project=cls.project, name="target question", variable_name="tgt_question"
        )
        cls.source_question = OpenQuestion.objects.create(
            project=cls.project, name="source question", variable_name="src_question"
        )
        cls.other_question = OpenQuestion.objects.create(
            project=cls.project, name="source question", variable_name="other_question"
        )
        cls.source_item = QuestionItem.objects.create(
            question=cls.other_question, index=1, value=1
        )

    def _form(self, source):
        return FilterConditionForm(
            data={
                "index": 0,
                "combinator": FilterCondition.ConditionCombinators.AND,
                "source": source,
                "condition_operator": FilterCondition.ConditionOperators.EQUALS,
                "condition_value": "x",
            },
            project=self.project,
            target_object=self.target_question,
        )

    def test_save_sets_source_question_and_clears_others(self):
        form = self._form(f"{FilterSourceTypes.QUESTION}-{self.source_question.id}")
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.source_question_id, self.source_question.id)
        self.assertIsNone(instance.source_item)
        self.assertEqual(instance.source_identifier, str(self.source_question.id))
        self.assertEqual(instance.source_type, FilterSourceTypes.QUESTION)

    def test_save_sets_source_item_and_clears_others(self):
        form = self._form(f"{FilterSourceTypes.QUESTION_ITEM}-{self.source_item.id}")
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.source_item_id, self.source_item.id)
        self.assertIsNone(instance.source_question)
        self.assertEqual(instance.source_identifier, str(self.source_item.id))

    def test_save_sets_source_identifier_for_non_model_sources(self):
        """URL parameter / participant / donation sources aren't FKs."""
        form = self._form(f"{FilterSourceTypes.PARTICIPANT}-_briefing_consent")
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.source_identifier, "_briefing_consent")
        self.assertIsNone(instance.source_question)
        self.assertIsNone(instance.source_item)

    def test_save_with_variable_source_sets_identifier_to_variable_name(self):
        form = self._form(f"{FilterSourceTypes.PARTICIPANT}-_start_time")
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertIsNone(instance.source_question)
        self.assertIsNone(instance.source_item)
        self.assertEqual(instance.source_identifier, "_start_time")

    def test_editing_switches_source_type_correctly(self):
        """Regression guard: switching from a question source to an item source
        on an existing instance must clear the stale FK, not just add the new one."""
        existing = FilterCondition.objects.create(
            source_question=self.source_question,
            source_type=FilterSourceTypes.QUESTION,
        )
        form = FilterConditionForm(
            data={
                "index": 0,
                "combinator": FilterCondition.ConditionCombinators.AND,
                "source": f"{FilterSourceTypes.QUESTION_ITEM}-{self.source_item.id}",
                "condition_operator": FilterCondition.ConditionOperators.EQUALS,
                "condition_value": "x",
            },
            project=self.project,
            target_object=self.target_question,
            instance=existing,
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertIsNone(instance.source_question)
        self.assertEqual(instance.source_item_id, self.source_item.id)


class FilterConditionFormInitialValueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )
        cls.target = OpenQuestion.objects.create(
            project=cls.project, name="target question", variable_name="tgt_question"
        )
        cls.source_q = OpenQuestion.objects.create(
            project=cls.project, name="source question", variable_name="src_question"
        )
        cls.other_question = OpenQuestion.objects.create(
            project=cls.project, name="source question", variable_name="other_question"
        )
        cls.source_item = QuestionItem.objects.create(
            question=cls.other_question, index=1, value=1
        )

    def test_initial_source_built_from_existing_question_instance(self):

        existing = FilterCondition.objects.create(
            source_question=self.source_q, source_type=FilterSourceTypes.QUESTION
        )
        form = FilterConditionForm(
            project=self.project, target_object=self.target, instance=existing
        )
        self.assertEqual(
            form.initial["source"], f"{FilterSourceTypes.QUESTION}-{self.source_q.id}"
        )
