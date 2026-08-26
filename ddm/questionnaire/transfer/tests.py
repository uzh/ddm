import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.urls import reverse

from ddm.core.utils.transfer.id_mapping import LocalIdAllocator
from ddm.datadonation.models import DonationBlueprint
from ddm.datadonation.schemas import JSONParserConfig
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import (
    FilterCondition,
    MatrixQuestion,
    QuestionBase,
    QuestionItem,
    ScalePoint,
    SingleChoiceQuestion,
    Transition,
)
from ddm.questionnaire.transfer.services import (
    build_questions,
    copy_question,
    export_questions,
    serialize_questions,
)

User = get_user_model()


def make_project(name: str, slug: str, owner: ResearchProfile) -> DonationProject:
    return DonationProject.objects.create(name=name, slug=slug, owner=owner)


class TestSerializeQuestions(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = make_project("Project", "project", profile)
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name="linked_bp",
            expected_fields='"a"',
            parser_config=JSONParserConfig().model_dump(),
        )
        cls.linked_q = Transition.objects.create(
            project=cls.project,
            blueprint=cls.blueprint,
            name="linked",
            variable_name="linked_q",
            page=1,
            index=1,
        )

    def test_blueprint_local_id_populated_when_requested(self):
        data = serialize_questions(
            self.project, LocalIdAllocator(), include_blueprint_ref=True
        )
        q = next(q for q in data if q["name"] == "linked")
        self.assertIsNotNone(q["blueprint_local_id"])
        self.assertIsNone(q["blueprint_name"])

    def test_blueprint_name_populated_in_standalone_mode(self):
        data = serialize_questions(
            self.project, LocalIdAllocator(), include_blueprint_ref=False
        )
        q = next(q for q in data if q["name"] == "linked")
        self.assertIsNone(q["blueprint_local_id"])
        self.assertEqual(q["blueprint_name"], "linked_bp")


class TestBuildQuestionsBlueprintNameResolution(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.source_project = make_project("Source", "source", profile)
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.source_project,
            name="linked_bp",
            expected_fields='"a"',
            parser_config=JSONParserConfig().model_dump(),
        )
        Transition.objects.create(
            project=cls.source_project,
            blueprint=cls.blueprint,
            name="linked question",
            variable_name="linked_q",
            page=1,
            index=1,
        )
        cls.owner_profile = profile

    def test_match_resolves_blueprint_fk(self):
        target_project = make_project("Target A", "target-a", self.owner_profile)
        DonationBlueprint.objects.create(
            project=target_project,
            name="linked_bp",
            expected_fields='"a"',
            parser_config=JSONParserConfig().model_dump(),
        )
        data = serialize_questions(
            self.source_project, LocalIdAllocator(), include_blueprint_ref=False
        )
        created, warnings = build_questions(data, target_project)
        self.assertEqual(warnings, [])
        new_q = created[0]
        self.assertEqual(new_q.blueprint.name, "linked_bp")
        self.assertEqual(new_q.blueprint.project, target_project)

    def test_no_match_leaves_blueprint_unset_and_warns(self):
        target_project = make_project("Target B", "target-b", self.owner_profile)
        data = serialize_questions(
            self.source_project, LocalIdAllocator(), include_blueprint_ref=False
        )
        created, warnings = build_questions(data, target_project)
        self.assertEqual(len(warnings), 1)
        self.assertIn("linked_bp", warnings[0])
        new_q = created[0]
        self.assertIsNone(new_q.blueprint)


class TestBuildQuestionsFilterConditionRemap(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.source_project = make_project("Source", "source", profile)
        cls.owner_profile = profile

        cls.q1 = Transition.objects.create(
            project=cls.source_project,
            name="q1",
            variable_name="q1",
            page=1,
            index=1,
        )
        cls.q2 = Transition.objects.create(
            project=cls.source_project,
            name="q2",
            variable_name="q2",
            page=1,
            index=2,
        )
        # q2 is shown only if q1 == 1 (FK-based source).
        FilterCondition.objects.create(
            target_question=cls.q2,
            source_type="question",
            source_question=cls.q1,
            source_identifier=str(cls.q1.pk),
            condition_operator="==",
            condition_value=1,
            index=1,
        )
        # q1 is shown only if the "_url_ref" url parameter equals "x"
        # (identifier-based source, no FK).
        FilterCondition.objects.create(
            target_question=cls.q1,
            source_type="url_parameter",
            source_identifier="_url_ref",
            condition_operator="==",
            condition_value="x",
            index=1,
        )

    def test_fk_source_and_identifier_source_both_survive_a_fresh_import(self):
        target_project = make_project("Target", "target", self.owner_profile)
        data = serialize_questions(
            self.source_project, LocalIdAllocator(), include_blueprint_ref=False
        )
        created, warnings = build_questions(data, target_project)
        self.assertEqual(warnings, [])

        new_q1 = next(q for q in created if q.variable_name == "q1")
        new_q2 = next(q for q in created if q.variable_name == "q2")

        fk_fc = FilterCondition.objects.get(target_question=new_q2)
        self.assertEqual(fk_fc.source_question_id, new_q1.pk)
        self.assertEqual(fk_fc.source_identifier, str(new_q1.pk))

        identifier_fc = FilterCondition.objects.get(target_question=new_q1)
        self.assertEqual(identifier_fc.source_type, "url_parameter")
        self.assertEqual(identifier_fc.source_identifier, "_url_ref")
        self.assertIsNone(identifier_fc.source_question)

    def test_item_target_filter_condition_remaps_too(self):
        sc = SingleChoiceQuestion.objects.create(
            project=self.source_project,
            name="choice",
            variable_name="choice",
            page=2,
            index=1,
        )
        item = QuestionItem.objects.create(question=sc, index=1, value=1, label="A")
        FilterCondition.objects.create(
            target_item=item,
            source_type="question",
            source_question=self.q1,
            source_identifier=str(self.q1.pk),
            condition_operator="==",
            condition_value=1,
            index=1,
        )

        target_project = make_project("Target2", "target2", self.owner_profile)
        data = serialize_questions(
            self.source_project, LocalIdAllocator(), include_blueprint_ref=False
        )
        created, _ = build_questions(data, target_project)

        new_choice = next(q for q in created if q.variable_name == "choice")
        new_item = new_choice.questionitem_set.get(value=1)
        fc = FilterCondition.objects.get(target_item=new_item)
        self.assertEqual(fc.source_question.variable_name, "q1")


class TestCopyQuestion(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="copyowner", password="123", email="copyowner@mail.com"
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
        # source must still point at the ORIGINAL item
        self.assertEqual(new_filter.source_item, self.item_a)
        self.assertNotEqual(new_filter.pk, self.question_filter.pk)

    def test_item_filter_condition_relinked_target_but_source_preserved(self):
        new_q = copy_question(self.question)
        new_item_b = new_q.questionitem_set.get(index=2)
        new_filter = FilterCondition.objects.get(target_item=new_item_b)
        self.assertEqual(new_filter.target_item, new_item_b)
        # source must still point at the ORIGINAL question
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


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestQuestionnaireExportImportViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner)

        cls.source_project = DonationProject.objects.create(
            name="Source", slug="source", owner=cls.owner_profile
        )
        cls.target_project = DonationProject.objects.create(
            name="Target", slug="target", owner=cls.owner_profile
        )
        Transition.objects.create(
            project=cls.source_project,
            name="q1",
            variable_name="q1",
            page=1,
            index=1,
        )

    def test_export_returns_downloadable_json(self):
        self.client.login(username="owner", password="123")
        response = self.client.get(
            reverse("ddm_questionnaire:export", args=[self.source_project.url_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        data = json.loads(response.content)
        self.assertEqual(data["export_kind"], "questionnaire")
        self.assertEqual(len(data["questions"]), 1)

    def test_import_into_different_project(self):
        self.client.login(username="owner", password="123")
        payload = export_questions(self.source_project)
        raw = json.dumps(payload).encode("utf-8")
        upload = SimpleUploadedFile("q.json", raw, content_type="application/json")

        response = self.client.post(
            reverse("ddm_questionnaire:import", args=[self.target_project.url_id]),
            data={"file": upload},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.target_project.questionbase_set.filter(variable_name="q1").exists()
        )
