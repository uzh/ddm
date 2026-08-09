from datetime import timedelta

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone

from ddm.questionnaire.models import QuestionnaireResponse


class TestDeduplicateResponsesMigration(TransactionTestCase):
    """Verifies the 0017 data migration keeps only the most recent
    QuestionnaireResponse per (project, participant) before the unique
    constraint is added, so downstream databases with pre-existing
    duplicates (e.g. from a past double-submit) can migrate safely.
    """

    # ddm_projects/ddm_participation are pinned to their latest migration in
    # both lists (only ddm_questionnaire should actually move between
    # 0016 and 0017) - otherwise MigrationExecutor.migrate() may roll them
    # back further than intended to satisfy the dependency graph.
    migrate_from = [
        ("ddm_questionnaire", "0016_remove_questionbase_required_and_more"),
        ("ddm_projects", "0009_donationproject_background_color_and_more"),
        ("ddm_participation", "0003_participant_url_parameter"),
    ]
    migrate_to = [
        ("ddm_questionnaire", "0017_questionnaireresponse_is_complete_and_more"),
        ("ddm_projects", "0009_donationproject_background_color_and_more"),
        ("ddm_participation", "0003_participant_url_parameter"),
    ]

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        User = old_apps.get_model("auth", "User")
        ResearchProfile = old_apps.get_model("ddm_projects", "ResearchProfile")
        DonationProject = old_apps.get_model("ddm_projects", "DonationProject")
        Participant = old_apps.get_model("ddm_participation", "Participant")
        QuestionnaireResponse = old_apps.get_model(
            "ddm_questionnaire", "QuestionnaireResponse"
        )

        now = timezone.now()

        user = User.objects.create(username="owner", email="owner@mail.com")
        profile = ResearchProfile.objects.create(user=user)
        self.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )
        self.dupe_participant = Participant.objects.create(
            project=self.project, start_time=now, external_id="a" * 24
        )
        self.clean_participant = Participant.objects.create(
            project=self.project, start_time=now, external_id="b" * 24
        )

        # Duplicate rows for one participant - the case the migration must fix.
        self.older = QuestionnaireResponse.objects.create(
            project=self.project,
            participant=self.dupe_participant,
            data=b"older",
            time_submitted=now - timedelta(days=1),
        )
        self.newer = QuestionnaireResponse.objects.create(
            project=self.project,
            participant=self.dupe_participant,
            data=b"newer",
            time_submitted=now,
        )
        # A single, already-clean row for the other participant.
        QuestionnaireResponse.objects.create(
            project=self.project,
            participant=self.clean_participant,
            data=b"clean",
            time_submitted=now - timedelta(days=1),
        )

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.migrate_to)

    def tearDown(self):
        # Reset to the latest migration state for subsequent tests.
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_only_most_recent_duplicate_row_survives(self):
        rows = QuestionnaireResponse.objects.filter(
            project_id=self.project.pk, participant_id=self.dupe_participant.pk
        )
        self.assertEqual(rows.count(), 1)
        self.assertEqual(bytes(rows.first().data), b"newer")

    def test_non_duplicate_row_is_untouched(self):
        rows = QuestionnaireResponse.objects.filter(
            project_id=self.project.pk, participant_id=self.clean_participant.pk
        )
        self.assertEqual(rows.count(), 1)
        self.assertEqual(bytes(rows.first().data), b"clean")

    def test_is_complete_defaults_true_for_existing_rows(self):
        for row in QuestionnaireResponse.objects.all():
            self.assertTrue(row.is_complete)
