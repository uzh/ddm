from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, models
from django.test import TestCase
from django.utils import timezone

from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.datadonation.schemas import JSONParserConfig
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class TestParticipantExternalIdGeneration(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Project", slug="base-regex-2", owner=profile
        )

    def test_new_participant_gets_external_id(self):
        """New participant should be assigned an external_id."""
        participant = Participant.objects.create(
            project=self.project, start_time=timezone.now()
        )
        self.assertEqual(len(participant.external_id), 24)

    def test_retry_on_integrity_error(self):
        """Should retry with new ID if IntegrityError occurs."""
        participant = Participant(project=self.project, start_time=timezone.now())

        call_count = 0
        original_save = models.Model.save

        def mock_save(self, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first 2 attempts
                msg = "duplicate key"
                raise IntegrityError(msg)
            return original_save(self, *args, **kwargs)

        with patch.object(models.Model, "save", mock_save):
            participant.save()

        self.assertEqual(call_count, 3)
        self.assertEqual(len(participant.external_id), 24)


class TestGetDonationInfo(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name="Project", slug="donation-info", owner=profile
        )
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name="blueprint",
            display_name="Blueprint",
            expected_fields='"a"',
            display_position=1,
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )
        cls.participant = Participant.objects.create(
            project=cls.project, start_time=timezone.now()
        )

        states_and_consent = [
            (DataDonation.DataExtractionState.DATA_EXTRACTED, True),
            (DataDonation.DataExtractionState.DATA_EXTRACTED, False),
            (DataDonation.DataExtractionState.NOT_ATTEMPTED, False),
            (DataDonation.DataExtractionState.NO_DATA_EXTRACTED, False),
            (DataDonation.DataExtractionState.FAILED, False),
        ]
        for state, consent in states_and_consent:
            DataDonation.objects.create(
                project=cls.project,
                blueprint=cls.blueprint,
                participant=cls.participant,
                time_submitted=timezone.now(),
                consent=consent,
                data_extraction_state=state,
                n_data_entries=0,
                data=[],
            )

    def test_donation_info_distinguishes_not_attempted_from_no_data_extracted(self):
        """n_pending and n_no_data_extracted must count distinct states."""
        info = self.participant.get_donation_info()

        self.assertEqual(info["n_success"], 2)
        self.assertEqual(info["n_pending"], 1)
        self.assertEqual(info["n_failed"], 1)
        self.assertEqual(info["n_consent"], 1)
        self.assertEqual(info["n_no_consent"], 1)
        self.assertEqual(info["n_no_data_extracted"], 1)
