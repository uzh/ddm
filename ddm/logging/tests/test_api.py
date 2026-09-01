from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.datadonation.schemas import JSONParserConfig
from ddm.logging.api.views import SESSION_LOST_DESCRIPTION
from ddm.logging.models import EventLogEntry, ExceptionLogEntry, ExceptionRaisers
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class TestExceptionAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)

        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )

        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name="zip file uploader",
            upload_type=FileUploader.UploadTypes.ZIP_FILE,
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name="valid blueprint",
            description="some description",
            expected_fields='"some field"',
            file_uploader=cls.file_uploader,
            parser_config=JSONParserConfig().model_dump(),
        )

        cls.post_url = reverse("ddm_logging:exceptions_api", args=[cls.project.url_id])
        cls.post_data = {
            "blueprint": cls.blueprint.pk,
            "status_code": 1,
            "raised_by": ExceptionRaisers.SERVER,
            "message": "Some message.",
        }

    def test_post_without_participant(self):
        client = Client()

        exceptions_count_before = ExceptionLogEntry.objects.count()
        client.post(self.post_url, self.post_data)

        exceptions_count_after = ExceptionLogEntry.objects.count()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))

    def test_valid_post(self):
        client = Client()
        client.get(reverse("ddm_participation:briefing", args=[self.project.slug]))

        exceptions_count_before = ExceptionLogEntry.objects.count()
        client.post(self.post_url, self.post_data)

        exceptions_count_after = ExceptionLogEntry.objects.count()
        self.assertEqual(exceptions_count_before, (exceptions_count_after - 1))

    def test_post_links_participant_from_session(self):
        client = Client()
        client.get(reverse("ddm_participation:briefing", args=[self.project.slug]))
        session_participant_id = client.session[f"project-{self.project.pk}"][
            "participant_id"
        ]

        client.post(self.post_url, self.post_data)

        entry = ExceptionLogEntry.objects.latest("pk")
        self.assertEqual(entry.participant_id, session_participant_id)
        self.assertFalse(
            EventLogEntry.objects.filter(description=SESSION_LOST_DESCRIPTION).exists()
        )

    def test_post_without_session_but_known_uploader_logs_event(self):
        client = Client()
        data = {
            **self.post_data,
            "uploader": self.file_uploader.pk,
            "date": "2026-09-01T10:00:00Z",
        }

        response = client.post(self.post_url, data)

        self.assertEqual(response.status_code, 201)
        entry = ExceptionLogEntry.objects.latest("pk")
        self.assertIsNone(entry.participant)
        self.assertEqual(
            EventLogEntry.objects.filter(
                project=self.project, description=SESSION_LOST_DESCRIPTION
            ).count(),
            1,
        )

    def test_missing_session_event_log_deduplicated_per_batch(self):
        client = Client()
        data = {
            **self.post_data,
            "uploader": self.file_uploader.pk,
            "date": "2026-09-01T10:00:00Z",
        }

        client.post(self.post_url, data)
        client.post(self.post_url, {**data, "status_code": "EXTRACTION_STATS"})

        self.assertEqual(ExceptionLogEntry.objects.count(), 2)
        self.assertEqual(
            EventLogEntry.objects.filter(
                project=self.project, description=SESSION_LOST_DESCRIPTION
            ).count(),
            1,
        )

    def test_post_without_uploader_does_not_log_event(self):
        client = Client()

        client.post(self.post_url, self.post_data)

        self.assertFalse(
            EventLogEntry.objects.filter(description=SESSION_LOST_DESCRIPTION).exists()
        )

    def test_post_with_deleted_participant_in_session(self):
        client = Client()
        client.get(reverse("ddm_participation:briefing", args=[self.project.slug]))
        Participant.objects.filter(
            pk=client.session[f"project-{self.project.pk}"]["participant_id"]
        ).delete()

        exceptions_count_before = ExceptionLogEntry.objects.count()
        response = client.post(self.post_url, self.post_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ExceptionLogEntry.objects.count(), exceptions_count_before + 1)
        self.assertIsNone(ExceptionLogEntry.objects.latest("pk").participant)

    def test_post_to_unknown_project_returns_404(self):
        client = Client()
        url = reverse("ddm_logging:exceptions_api", args=["does-not-exist"])

        response = client.post(url, self.post_data)

        self.assertEqual(response.status_code, 404)


class TestEventLogAPIView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner_creds = {
            "username": "owner",
            "password": "testpass123",
            "email": "owner@mail.com",
        }
        cls.owner_user = User.objects.create_user(**cls.owner_creds)
        cls.owner_user.is_staff = True
        cls.owner_user.save()
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner_user)

        cls.other_creds = {
            "username": "other",
            "password": "testpass123",
            "email": "other@mail.com",
        }
        cls.other_user = User.objects.create_user(**cls.other_creds)
        cls.other_user.is_staff = True
        cls.other_user.save()
        cls.other_profile = ResearchProfile.objects.create(user=cls.other_user)

        cls.non_staff_creds = {
            "username": "nonstaff",
            "password": "testpass123",
            "email": "nonstaff@mail.com",
        }
        cls.non_staff_user = User.objects.create_user(**cls.non_staff_creds)
        cls.non_staff_profile = ResearchProfile.objects.create(user=cls.non_staff_user)

        cls.project = DonationProject.objects.create(
            name="Test Project", slug="test-project", owner=cls.owner_profile
        )

        cls.event_log_1 = EventLogEntry.objects.create(
            project=cls.project,
            description="Token regenerated",
            message="API token was regenerated by owner.",
            date=timezone.now(),
        )
        cls.event_log_2 = EventLogEntry.objects.create(
            project=cls.project,
            description="Data downloaded",
            message="Project data was downloaded.",
            date=timezone.now(),
        )
        cls.event_log_3 = EventLogEntry.objects.create(
            project=cls.project,
            description="Participant deleted",
            message="Participant XYZ was removed.",
            date=timezone.now(),
        )

        cls.api_url = reverse("ddm_logging:event_logs_api", args=[cls.project.url_id])

    def test_unauthenticated_access_denied(self):
        client = APIClient()
        response = client.get(self.api_url)
        self.assertEqual(response.status_code, 403)

    def test_non_owner_access_denied(self):
        client = APIClient()
        client.login(**self.non_staff_creds)
        response = client.get(self.api_url)
        self.assertEqual(response.status_code, 403)

    def test_non_staff_owner_access_denied(self):
        project = DonationProject.objects.create(
            name="Non Staff Project",
            slug="non-staff-project",
            owner=self.other_profile,
        )
        url = reverse("ddm_logging:event_logs_api", args=[project.url_id])
        client = APIClient()
        client.login(**self.non_staff_creds)
        response = client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_owner_access_allowed(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url)
        self.assertEqual(response.status_code, 200)

    def test_response_format(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url)
        self.assertIn("total", response.data)
        self.assertIn("rows", response.data)
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(len(response.data["rows"]), 3)

    def test_serializer_fields(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url)
        row = response.data["rows"][0]
        self.assertIn("date", row)
        self.assertIn("description", row)
        self.assertIn("message", row)

    def test_pagination(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"limit": 2, "offset": 0})
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(len(response.data["rows"]), 2)

        response = client.get(self.api_url, {"limit": 2, "offset": 2})
        self.assertEqual(len(response.data["rows"]), 1)

    def test_filter_by_description(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"description": "Token"})
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["rows"][0]["description"], "Token regenerated")

    def test_filter_by_message(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"message": "XYZ"})
        self.assertEqual(response.data["total"], 1)
        self.assertIn("XYZ", response.data["rows"][0]["message"])

    def test_ordering_ascending(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"ordering": "description"})
        descriptions = [row["description"] for row in response.data["rows"]]
        self.assertEqual(descriptions, sorted(descriptions))

    def test_ordering_descending(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"ordering": "-description"})
        descriptions = [row["description"] for row in response.data["rows"]]
        self.assertEqual(descriptions, sorted(descriptions, reverse=True))

    def test_nonexistent_project_returns_404(self):
        client = APIClient()
        client.login(**self.owner_creds)
        url = reverse("ddm_logging:event_logs_api", args=["nonexistent-id"])
        response = client.get(url)
        self.assertEqual(response.status_code, 404)


class TestExceptionLogAPIView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner_creds = {
            "username": "owner",
            "password": "testpass123",
            "email": "owner@mail.com",
        }
        cls.owner_user = User.objects.create_user(**cls.owner_creds)
        cls.owner_user.is_staff = True
        cls.owner_user.save()
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner_user)

        cls.other_creds = {
            "username": "other",
            "password": "testpass123",
            "email": "other@mail.com",
        }
        cls.other_user = User.objects.create_user(**cls.other_creds)
        cls.other_user.is_staff = False
        cls.other_user.save()

        cls.project = DonationProject.objects.create(
            name="Test Project", slug="test-project", owner=cls.owner_profile
        )

        cls.participant = Participant.objects.create(
            project=cls.project, start_time=timezone.now()
        )

        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name="Test Uploader",
            upload_type=FileUploader.UploadTypes.ZIP_FILE,
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name="Test Blueprint",
            description="Test description",
            expected_fields='"field1"',
            file_uploader=cls.file_uploader,
            parser_config=JSONParserConfig().model_dump(),
        )

        cls.exception_log_1 = ExceptionLogEntry.objects.create(
            project=cls.project,
            participant=cls.participant,
            blueprint=cls.blueprint,
            exception_type="ValidationError",
            raised_by=ExceptionRaisers.SERVER,
            message="Validation failed for field X.",
            date=timezone.now(),
        )
        cls.exception_log_2 = ExceptionLogEntry.objects.create(
            project=cls.project,
            participant=None,
            blueprint=None,
            exception_type="NetworkError",
            raised_by=ExceptionRaisers.CLIENT,
            message="Network connection lost.",
            date=timezone.now(),
        )
        cls.exception_log_3 = ExceptionLogEntry.objects.create(
            project=cls.project,
            participant=cls.participant,
            blueprint=cls.blueprint,
            exception_type="ParseError",
            raised_by=ExceptionRaisers.SERVER,
            message="Failed to parse JSON file.",
            date=timezone.now(),
        )

        cls.api_url = reverse(
            "ddm_logging:exception_logs_api", args=[cls.project.url_id]
        )

    def test_unauthenticated_access_denied(self):
        client = APIClient()
        response = client.get(self.api_url)
        self.assertEqual(response.status_code, 403)

    def test_non_owner_access_denied(self):
        client = APIClient()
        client.login(**self.other_creds)
        response = client.get(self.api_url)
        self.assertEqual(response.status_code, 403)

    def test_owner_access_allowed(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url)
        self.assertEqual(response.status_code, 200)

    def test_response_format(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url)
        self.assertIn("total", response.data)
        self.assertIn("rows", response.data)
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(len(response.data["rows"]), 3)

    def test_serializer_fields(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url)
        row = response.data["rows"][0]
        self.assertIn("date", row)
        self.assertIn("participant", row)
        self.assertIn("exception_type", row)
        self.assertIn("raised_by", row)
        self.assertIn("blueprint", row)
        self.assertIn("message", row)

    def test_participant_serialized_as_external_id(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"exception_type": "ValidationError"})
        row = response.data["rows"][0]
        self.assertEqual(row["participant"], self.participant.external_id)

    def test_blueprint_serialized_as_name(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"exception_type": "ValidationError"})
        row = response.data["rows"][0]
        self.assertEqual(row["blueprint"], self.blueprint.name)

    def test_null_participant_serialized_correctly(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"exception_type": "NetworkError"})
        row = response.data["rows"][0]
        self.assertIsNone(row["participant"])

    def test_null_blueprint_serialized_correctly(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"exception_type": "NetworkError"})
        row = response.data["rows"][0]
        self.assertIsNone(row["blueprint"])

    def test_pagination(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"limit": 2, "offset": 0})
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(len(response.data["rows"]), 2)

        response = client.get(self.api_url, {"limit": 2, "offset": 2})
        self.assertEqual(len(response.data["rows"]), 1)

    def test_filter_by_exception_type(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"exception_type": "Validation"})
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["rows"][0]["exception_type"], "ValidationError")

    def test_filter_by_raised_by(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"raised_by": "client"})
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["rows"][0]["raised_by"], "client")

    def test_filter_by_message(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"message": "JSON"})
        self.assertEqual(response.data["total"], 1)
        self.assertIn("JSON", response.data["rows"][0]["message"])

    def test_filter_by_participant(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(
            self.api_url, {"participant": self.participant.external_id[:8]}
        )
        self.assertEqual(response.data["total"], 2)

    def test_filter_by_blueprint(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"blueprint": "Test Blueprint"})
        self.assertEqual(response.data["total"], 2)

    def test_ordering_by_exception_type(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"ordering": "exception_type"})
        types = [row["exception_type"] for row in response.data["rows"]]
        self.assertEqual(types, sorted(types))

    def test_ordering_by_exception_type_descending(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"ordering": "-exception_type"})
        types = [row["exception_type"] for row in response.data["rows"]]
        self.assertEqual(types, sorted(types, reverse=True))

    def test_ordering_by_participant(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"ordering": "participant__external_id"})
        self.assertEqual(response.status_code, 200)
        # Verify ordering works (nulls may sort differently by DB)
        participants = [row["participant"] for row in response.data["rows"]]
        non_null = [p for p in participants if p is not None]
        self.assertEqual(non_null, sorted(non_null))

    def test_ordering_by_blueprint(self):
        client = APIClient()
        client.login(**self.owner_creds)
        response = client.get(self.api_url, {"ordering": "blueprint__name"})
        self.assertEqual(response.status_code, 200)
        # Verify ordering works (nulls may sort differently by DB)
        blueprints = [row["blueprint"] for row in response.data["rows"]]
        non_null = [b for b in blueprints if b is not None]
        self.assertEqual(non_null, sorted(non_null))

    def test_nonexistent_project_returns_404(self):
        client = APIClient()
        client.login(**self.owner_creds)
        url = reverse("ddm_logging:exception_logs_api", args=["nonexistent-id"])
        response = client.get(url)
        self.assertEqual(response.status_code, 404)
