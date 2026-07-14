from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, models
from django.test import TestCase
from django.utils import timezone

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
