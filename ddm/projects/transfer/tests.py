import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from ddm.core.utils.transfer.schema import (
    EXPORT_KIND_PROJECT,
    TransferValidationError,
    validate_envelope,
)
from ddm.datadonation.models import (
    BlueprintFilePath,
    DonationBlueprint,
    DonationInstruction,
    ExtractionField,
    FileUploader,
    ProcessingRule,
)
from ddm.datadonation.schemas import JSONParserConfig
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.projects.transfer import build_project, export_project
from ddm.questionnaire.models import (
    FilterCondition,
    QuestionItem,
    SingleChoiceQuestion,
    Transition,
)

User = get_user_model()


def build_reference_project() -> DonationProject:
    """
    Builds a project exercising every cross-reference the transfer engine
    has to handle: a backup blueprint, extraction fields/rules, a general
    question, a blueprint-linked question, item-level and question-level
    filter conditions (both FK-based and identifier-based sources).
    """
    user = User.objects.create_user(
        username="owner", password="123", email="owner@mail.com"
    )
    profile = ResearchProfile.objects.create(user=user)
    project = DonationProject.objects.create(
        name="Reference Project",
        slug="reference-project",
        owner=profile,
        contact_information="contact info",
        data_protection_statement="dp statement",
        briefing_text="briefing",
        debriefing_text="debriefing",
        primary_color="#123456",
    )

    uploader = FileUploader.objects.create(
        project=project,
        name="uploader",
        display_name="Uploader",
        upload_type=FileUploader.UploadTypes.SINGLE_FILE,
    )
    DonationInstruction.objects.create(file_uploader=uploader, index=1, text="Step 1")
    DonationInstruction.objects.create(file_uploader=uploader, index=2, text="Step 2")

    primary_bp = DonationBlueprint.objects.create(
        project=project,
        file_uploader=uploader,
        name="primary_blueprint",
        display_name="Primary",
        expected_fields='"field1"',
        parser_config=JSONParserConfig().model_dump(),
    )
    DonationBlueprint.objects.create(
        project=project,
        name="backup_blueprint",
        display_name="Backup",
        expected_fields='"field1"',
        parser_config=JSONParserConfig().model_dump(),
        backup_for=primary_bp,
        backup_priority=1,
    )
    field_a = ExtractionField.objects.create(
        blueprint=primary_bp, expected_name="fieldA"
    )
    ExtractionField.objects.create(blueprint=primary_bp, expected_name="fieldB")
    ProcessingRule.objects.create(
        blueprint=primary_bp,
        name="rule",
        field=field_a,
        execution_order=1,
        comparison_operator=ProcessingRule.ComparisonOperators.EQUAL,
        comparison_value="1",
    )
    # A rule with no associated field (field=SET_NULL) - must survive
    # export/import too, unlike the pre-existing copy_blueprint().
    ProcessingRule.objects.create(
        blueprint=primary_bp,
        name="fieldless rule",
        execution_order=2,
        comparison_operator=ProcessingRule.ComparisonOperators.EQUAL,
    )
    BlueprintFilePath.objects.create(
        blueprint=primary_bp, path="/data/file.json", is_regex=False, priority=1
    )

    sc_question = SingleChoiceQuestion.objects.create(
        project=project,
        blueprint=primary_bp,
        name="Choice question",
        variable_name="choice_q",
        page=1,
        index=1,
        text="Pick one",
    )
    item_a = QuestionItem.objects.create(
        question=sc_question, index=1, label="A", value=1
    )
    QuestionItem.objects.create(question=sc_question, index=2, label="B", value=2)

    general_question = Transition.objects.create(
        project=project,
        name="Transition question",
        variable_name="trans_q",
        page=2,
        index=1,
        text="Now the next part.",
    )

    # Question-level filter, FK source (another question).
    FilterCondition.objects.create(
        target_question=general_question,
        source_type="question",
        source_question=sc_question,
        source_identifier=str(sc_question.pk),
        condition_operator="==",
        condition_value=1,
        index=1,
    )
    # Item-level filter, identifier-based source (no FK).
    FilterCondition.objects.create(
        target_item=item_a,
        source_type="url_parameter",
        source_identifier="_url_campaign",
        condition_operator="==",
        condition_value="x",
        index=1,
    )

    return project


class TestSerializeProject(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = build_reference_project()

    def test_no_real_pks_leak_into_payload(self):
        data = export_project(self.project)
        payload_str = json.dumps(data)
        # The project pk itself should not appear anywhere as a bare value.
        self.assertNotIn(f'"id": {self.project.pk}', payload_str)

    def test_excludes_identity_and_secret_fields(self):
        data = export_project(self.project)
        for key in ("id", "url_id", "slug", "owner", "public_key", "date_created"):
            self.assertNotIn(key, data["project"])
        self.assertNotIn("img_header_left", data["project"])
        self.assertNotIn("img_header_right", data["project"])

    def test_envelope_shape(self):
        data = export_project(self.project)
        self.assertEqual(data["export_kind"], EXPORT_KIND_PROJECT)
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(len(data["file_uploaders"]), 1)
        self.assertEqual(len(data["blueprints"]), 2)
        self.assertEqual(len(data["questions"]), 2)

    def test_backup_for_resolves_to_sibling_local_id(self):
        data = export_project(self.project)
        by_name = {bp["name"]: bp for bp in data["blueprints"]}
        primary_local_id = by_name["primary_blueprint"]["local_id"]
        self.assertEqual(
            by_name["backup_blueprint"]["backup_for_local_id"], primary_local_id
        )
        self.assertIsNone(by_name["primary_blueprint"]["backup_for_local_id"])

    def test_fieldless_processing_rule_included(self):
        data = export_project(self.project)
        primary = next(
            bp for bp in data["blueprints"] if bp["name"] == "primary_blueprint"
        )
        self.assertEqual(len(primary["processing_rules"]), 2)
        fieldless = [
            r for r in primary["processing_rules"] if r["field_local_id"] is None
        ]
        self.assertEqual(len(fieldless), 1)

    def test_question_blueprint_link_uses_local_id(self):
        data = export_project(self.project)
        choice_q = next(q for q in data["questions"] if q["name"] == "Choice question")
        primary_local_id = next(
            bp["local_id"]
            for bp in data["blueprints"]
            if bp["name"] == "primary_blueprint"
        )
        self.assertEqual(choice_q["blueprint_local_id"], primary_local_id)
        self.assertIsNone(choice_q["blueprint_name"])

    def test_filter_condition_target_and_source_use_local_ids(self):
        data = export_project(self.project)
        transition_q = next(
            q for q in data["questions"] if q["name"] == "Transition question"
        )
        choice_q = next(q for q in data["questions"] if q["name"] == "Choice question")

        fc = transition_q["filter_conditions"][0]
        self.assertEqual(fc["target_local_id"], transition_q["local_id"])
        self.assertEqual(fc["source_local_id"], choice_q["local_id"])
        self.assertIsNone(fc["source_identifier"])

        item_fc = choice_q["filter_conditions"][0]
        self.assertEqual(item_fc["source_type"], "url_parameter")
        self.assertEqual(item_fc["source_identifier"], "_url_campaign")
        self.assertIsNone(item_fc["source_local_id"])


class TestBuildProject(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.source_project = build_reference_project()
        cls.other_user = User.objects.create_user(
            username="importer", password="123", email="importer@mail.com"
        )
        cls.other_profile = ResearchProfile.objects.create(user=cls.other_user)

    def _build(self):
        payload = export_project(self.source_project)
        return build_project(
            payload,
            owner=self.other_profile,
            name="Imported Project",
            slug="imported-project",
        )

    def test_creates_distinct_project(self):
        new_project, warnings = self._build()
        self.assertNotEqual(new_project.pk, self.source_project.pk)
        self.assertEqual(new_project.name, "Imported Project")
        self.assertEqual(new_project.slug, "imported-project")
        self.assertEqual(new_project.owner, self.other_profile)
        self.assertEqual(warnings, [])

    def test_public_key_and_url_id_regenerated(self):
        new_project, _ = self._build()
        self.assertNotEqual(
            bytes(new_project.public_key), bytes(self.source_project.public_key)
        )
        self.assertNotEqual(new_project.url_id, self.source_project.url_id)

    def test_super_secret_always_false_regardless_of_source(self):
        self.source_project.secret_key = "a very very secret password"
        self.source_project.super_secret = True
        self.source_project.save()
        new_project, _ = self._build()
        self.assertFalse(new_project.super_secret)

    def test_no_access_token_carried_over(self):
        new_project, _ = self._build()
        self.assertFalse(hasattr(new_project, "projectaccesstoken"))

    def test_carries_over_content_fields(self):
        new_project, _ = self._build()
        self.assertEqual(new_project.contact_information, "contact info")
        self.assertEqual(new_project.briefing_text, "briefing")
        self.assertEqual(new_project.primary_color, "#123456")

    def test_nested_counts_match(self):
        new_project, _ = self._build()
        self.assertEqual(new_project.fileuploader_set.count(), 1)
        self.assertEqual(new_project.donationblueprint_set.count(), 2)
        self.assertEqual(new_project.questionbase_set.count(), 2)
        new_uploader = new_project.fileuploader_set.first()
        self.assertEqual(new_uploader.donationinstruction_set.count(), 2)

    def test_backup_for_repoints_to_new_sibling(self):
        new_project, _ = self._build()
        new_primary = new_project.donationblueprint_set.get(name="primary_blueprint")
        new_backup = new_project.donationblueprint_set.get(name="backup_blueprint")
        self.assertEqual(new_backup.backup_for_id, new_primary.pk)

    def test_processing_rules_including_fieldless_one_repoint_correctly(self):
        new_project, _ = self._build()
        new_primary = new_project.donationblueprint_set.get(name="primary_blueprint")
        rules = list(new_primary.processingrule_set.all())
        self.assertEqual(len(rules), 2)
        fieldless = [r for r in rules if r.field_id is None]
        self.assertEqual(len(fieldless), 1)
        with_field = next(r for r in rules if r.field_id is not None)
        self.assertEqual(with_field.field.blueprint_id, new_primary.pk)

    def test_blueprint_link_on_question_repoints_to_new_blueprint(self):
        new_project, _ = self._build()
        new_primary = new_project.donationblueprint_set.get(name="primary_blueprint")
        new_choice_q = new_project.questionbase_set.get(name="Choice question")
        self.assertEqual(new_choice_q.blueprint_id, new_primary.pk)

    def test_question_level_filter_condition_repoints_into_new_set(self):
        new_project, _ = self._build()
        new_choice_q = new_project.questionbase_set.get(name="Choice question")
        new_transition_q = new_project.questionbase_set.get(name="Transition question")
        fc = FilterCondition.objects.get(target_question=new_transition_q)
        self.assertEqual(fc.source_question_id, new_choice_q.pk)
        self.assertEqual(fc.source_identifier, str(new_choice_q.pk))

    def test_item_level_identifier_filter_condition_preserved(self):
        new_project, _ = self._build()
        new_choice_q = new_project.questionbase_set.get(name="Choice question")
        new_item_a = new_choice_q.questionitem_set.get(value=1)
        fc = FilterCondition.objects.get(target_item=new_item_a)
        self.assertEqual(fc.source_type, "url_parameter")
        self.assertEqual(fc.source_identifier, "_url_campaign")

    def test_original_project_untouched(self):
        self._build()
        self.source_project.refresh_from_db()
        self.assertEqual(self.source_project.donationblueprint_set.count(), 2)
        self.assertEqual(self.source_project.questionbase_set.count(), 2)


class TestProjectRoundTripViaJSON(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.source_project = build_reference_project()
        user = User.objects.create_user(
            username="importer2", password="123", email="importer2@mail.com"
        )
        cls.profile = ResearchProfile.objects.create(user=user)

    def test_json_dumps_loads_round_trip(self):
        payload = export_project(self.source_project)
        raw = json.dumps(payload)
        reloaded = json.loads(raw)

        new_project, warnings = build_project(
            reloaded,
            owner=self.profile,
            name="Round Trip Project",
            slug="round-trip-project",
        )
        self.assertEqual(warnings, [])
        self.assertEqual(new_project.donationblueprint_set.count(), 2)
        self.assertEqual(new_project.questionbase_set.count(), 2)


class TestSchemaValidation(TestCase):
    def test_valid_project_payload_passes(self):
        project = build_reference_project()
        data = export_project(project)
        validate_envelope(data, expected_kind=EXPORT_KIND_PROJECT)  # no raise

    def test_missing_schema_version_rejected(self):
        with self.assertRaises(TransferValidationError):
            validate_envelope(
                {"export_kind": "project"}, expected_kind=EXPORT_KIND_PROJECT
            )

    def test_wrong_export_kind_rejected(self):
        with self.assertRaises(TransferValidationError):
            validate_envelope(
                {"schema_version": 1, "export_kind": "blueprint"},
                expected_kind=EXPORT_KIND_PROJECT,
            )

    def test_dangling_backup_for_ref_is_tolerated_not_an_error(self):
        data = {
            "schema_version": 1,
            "export_kind": EXPORT_KIND_PROJECT,
            "project": {},
            "file_uploaders": [],
            "blueprints": [
                {
                    "local_id": "bp-1",
                    "name": "bp",
                    "backup_for_local_id": "bp-999",
                    "parser_config": {},
                    "expected_fields": "",
                    "file_paths": [],
                    "extraction_fields": [],
                    "processing_rules": [],
                }
            ],
            "questions": [],
        }
        validate_envelope(data, expected_kind=EXPORT_KIND_PROJECT)  # no raise

    def test_dangling_filter_condition_target_is_rejected(self):
        data = {
            "schema_version": 1,
            "export_kind": EXPORT_KIND_PROJECT,
            "project": {},
            "file_uploaders": [],
            "blueprints": [],
            "questions": [
                {
                    "local_id": "q-1",
                    "name": "q",
                    "variable_name": "q",
                    "items": [],
                    "filter_conditions": [
                        {
                            "target_local_id": "q-999",
                            "source_type": "system",
                            "source_identifier": "_something",
                        }
                    ],
                }
            ],
        }
        with self.assertRaises(TransferValidationError):
            validate_envelope(data, expected_kind=EXPORT_KIND_PROJECT)

    def test_dangling_filter_condition_fk_source_is_rejected(self):
        data = {
            "schema_version": 1,
            "export_kind": EXPORT_KIND_PROJECT,
            "project": {},
            "file_uploaders": [],
            "blueprints": [],
            "questions": [
                {
                    "local_id": "q-1",
                    "name": "q",
                    "variable_name": "q",
                    "items": [],
                    "filter_conditions": [
                        {
                            "target_local_id": "q-1",
                            "source_type": "question",
                            "source_local_id": "q-999",
                        }
                    ],
                }
            ],
        }
        with self.assertRaises(TransferValidationError):
            validate_envelope(data, expected_kind=EXPORT_KIND_PROJECT)


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestProjectExportView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner)
        cls.non_owner = User.objects.create_user(
            username="non-owner", password="123", email="non-owner@mail.com"
        )
        ResearchProfile.objects.create(user=cls.non_owner)
        cls.superuser = User.objects.create_superuser(
            username="super", password="123", email="super@mail.com"
        )
        ResearchProfile.objects.create(user=cls.superuser)

        cls.project = DonationProject.objects.create(
            name="Project", slug="project", owner=cls.owner_profile
        )

    def test_owner_can_export(self):
        self.client.login(username="owner", password="123")
        response = self.client.get(
            reverse("ddm_projects:export", args=[self.project.url_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("attachment", response["Content-Disposition"])
        data = json.loads(response.content)
        self.assertEqual(data["export_kind"], "project")

    def test_non_owner_gets_404(self):
        self.client.login(username="non-owner", password="123")
        response = self.client.get(
            reverse("ddm_projects:export", args=[self.project.url_id])
        )
        self.assertEqual(response.status_code, 404)

    def test_superuser_can_export_others_project(self):
        self.client.login(username="super", password="123")
        response = self.client.get(
            reverse("ddm_projects:export", args=[self.project.url_id])
        )
        self.assertEqual(response.status_code, 200)


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestProjectCopyView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner)
        cls.superuser = User.objects.create_superuser(
            username="super", password="123", email="super@mail.com"
        )
        cls.superuser_profile = ResearchProfile.objects.create(user=cls.superuser)
        cls.other_owner = User.objects.create_user(
            username="other", password="123", email="other@mail.com"
        )
        cls.other_profile = ResearchProfile.objects.create(user=cls.other_owner)

        cls.project = DonationProject.objects.create(
            name="Source",
            slug="source",
            owner=cls.owner_profile,
            contact_information="x",
            data_protection_statement="x",
            briefing_text="x",
            debriefing_text="x",
        )

    def test_owner_can_copy_into_own_account(self):
        self.client.login(username="owner", password="123")
        response = self.client.post(
            reverse("ddm_projects:copy", args=[self.project.url_id]),
            data={"name": "Copy", "slug": "copy-slug"},
        )
        self.assertEqual(response.status_code, 302)
        new_project = DonationProject.objects.get(slug="copy-slug")
        self.assertEqual(new_project.owner, self.owner_profile)

    def test_non_superuser_cannot_change_owner(self):
        self.client.login(username="owner", password="123")
        self.client.post(
            reverse("ddm_projects:copy", args=[self.project.url_id]),
            data={
                "name": "Copy",
                "slug": "copy-slug-2",
                "owner": self.other_profile.pk,
            },
        )
        new_project = DonationProject.objects.get(slug="copy-slug-2")
        self.assertEqual(new_project.owner, self.owner_profile)

    def test_superuser_can_pick_target_owner(self):
        self.client.login(username="super", password="123")
        response = self.client.post(
            reverse("ddm_projects:copy", args=[self.project.url_id]),
            data={
                "name": "Copy",
                "slug": "copy-slug-3",
                "owner": self.other_profile.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        new_project = DonationProject.objects.get(slug="copy-slug-3")
        self.assertEqual(new_project.owner, self.other_profile)

    def test_duplicate_slug_rejected_with_form_error(self):
        self.client.login(username="owner", password="123")
        response = self.client.post(
            reverse("ddm_projects:copy", args=[self.project.url_id]),
            data={"name": "Copy", "slug": "source"},  # collides with source
        )
        self.assertEqual(response.status_code, 200)  # re-renders form
        self.assertFalse(DonationProject.objects.filter(name="Copy").exists())


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestProjectImportView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner)

        cls.source_project = DonationProject.objects.create(
            name="Source",
            slug="a-different-source",
            owner=cls.owner_profile,
            contact_information="x",
            data_protection_statement="x",
            briefing_text="x",
            debriefing_text="x",
        )

    def _upload_file(self, data: dict) -> SimpleUploadedFile:
        raw = json.dumps(data).encode("utf-8")
        return SimpleUploadedFile("export.json", raw, content_type="application/json")

    def test_full_two_step_import_flow(self):
        self.client.login(username="owner", password="123")
        payload = export_project(self.source_project)

        step1 = self.client.post(
            reverse("ddm_projects:import"), data={"file": self._upload_file(payload)}
        )
        self.assertEqual(step1.status_code, 302)

        # Step 2 page should now render the review form.
        step2_get = self.client.get(reverse("ddm_projects:import"))
        self.assertContains(step2_get, "name")

        step2 = self.client.post(
            reverse("ddm_projects:import"),
            data={"name": "Imported", "slug": "imported-slug"},
        )
        self.assertEqual(step2.status_code, 302)
        new_project = DonationProject.objects.get(slug="imported-slug")
        self.assertEqual(new_project.owner, self.owner_profile)
        self.assertNotEqual(new_project.pk, self.source_project.pk)

    def test_malformed_file_rejected_at_step_one(self):
        self.client.login(username="owner", password="123")
        bad_file = self._upload_file({"schema_version": 1, "export_kind": "blueprint"})
        response = self.client.post(
            reverse("ddm_projects:import"), data={"file": bad_file}
        )
        self.assertEqual(response.status_code, 200)  # re-renders with error
        self.assertNotIn("ddm_project_import_payload", self.client.session)

    def test_submitting_step_two_without_prior_upload_redirects_to_step_one(self):
        self.client.login(username="owner", password="123")
        response = self.client.post(
            reverse("ddm_projects:import"),
            data={"name": "Imported", "slug": "orphan-slug"},
        )
        # No "file" key -> step is "upload" -> form is ProjectImportUploadForm,
        # which requires "file" -> re-renders with a validation error.
        self.assertEqual(response.status_code, 200)
        self.assertFalse(DonationProject.objects.filter(slug="orphan-slug").exists())
