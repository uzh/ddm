import csv
import io
import json

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime
from rest_framework.test import APIClient

from ddm.apis.serializers import (
    ParticipantSerializer,
    ProjectSerializer,
    ResponseSerializer,
    ResponseSerializerWithSnapshot,
)
from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.datadonation.schemas import JSONParserConfig
from ddm.participation.models import Participant
from ddm.participation.serializers import BlueprintSerializer
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import (
    MultiChoiceQuestion,
    OpenQuestion,
    QuestionItem,
    QuestionnaireResponse,
)

User = get_user_model()


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestAPIs(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.base_creds = {
            "username": "owner",
            "password": "123",
            "email": "owner@mail.com",
        }
        base_user = User.objects.create_user(**cls.base_creds)
        base_profile = ResearchProfile.objects.create(user=base_user)

        cls.no_perm_creds = {
            "username": "non-perm",
            "password": "123",
            "email": "non-perm@mail.com",
        }
        no_perm_user = User.objects.create_user(**cls.no_perm_creds)
        no_perm_profile = ResearchProfile.objects.create(user=no_perm_user)

        cls.project_base = DonationProject.objects.create(
            name="Base Project", slug="base", owner=base_profile
        )
        cls.project_no_quest = DonationProject.objects.create(
            name="Project no Questionnaire", slug="no-quest", owner=base_profile
        )
        cls.project_alt = DonationProject.objects.create(
            name="Alt Project", slug="alternative", owner=no_perm_profile
        )
        cls.project_super_secret = DonationProject.objects.create(
            name="Secret Project",
            slug="super-secret",
            owner=base_profile,
            super_secret=True,
        )

        cls.participant_a = Participant.objects.create(
            project=cls.project_base, start_time=timezone.now()
        )
        cls.participant_b = Participant.objects.create(
            project=cls.project_base, start_time=timezone.now()
        )
        cls.participant_c = Participant.objects.create(
            project=cls.project_alt, start_time=timezone.now()
        )

        cls.blueprint_a = DonationBlueprint.objects.create(
            project=cls.project_base,
            name="donation_blueprint",
            display_name="some name",
            expected_fields='"a", "b"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )
        cls.blueprint_b = DonationBlueprint.objects.create(
            project=cls.project_base,
            name="donation_blueprint_b",
            display_name="some name",
            expected_fields='"a", "b"',
            file_uploader=None,
            parser_config=JSONParserConfig().model_dump(),
        )

        cls.donation_pA_a = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_a,
            participant=cls.participant_a,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=2,
            data=["data1_pA_bpA", "data2_pA_bpA"],
        )
        cls.donation_pA_b = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_b,
            participant=cls.participant_a,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=2,
            data=["data1_pA_bpB", "data2_pA_bpB"],
        )

        cls.donation_pB_a = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_a,
            participant=cls.participant_b,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=2,
            data=["data1_pB_bpA", "data2_pB_bpA"],
        )
        cls.donation_pB_b = DataDonation.objects.create(
            project=cls.project_base,
            blueprint=cls.blueprint_b,
            participant=cls.participant_b,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=2,
            data=["data1_pB_bpB", "data2_pB_bpB"],
        )

        cls.question_open = OpenQuestion.objects.create(
            project=cls.project_base,
            name="open question",
            page=1,
            index=1,
            variable_name="open",
        )
        q = cls.question_open
        cls.q_response_a = QuestionnaireResponse.objects.create(
            project=cls.project_base,
            participant=cls.participant_a,
            time_submitted=timezone.now(),
            data=f'{{"{q.pk}": {{"response": "response_data", "question": "question text", "items": []}}}}',  # noqa: E501
        )

        cls.q_response_b = QuestionnaireResponse.objects.create(
            project=cls.project_base,
            participant=cls.participant_b,
            time_submitted=timezone.now(),
            data=f'{{"{q.pk}": {{"response": "response_data2", "question": "question text", "items": []}}}}',  # noqa: E501
        )

    def test_project_detail_api_get_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        expected_response = {
            "participants": [
                ParticipantSerializer(self.participant_a).data,
                ParticipantSerializer(self.participant_b).data,
            ],
            "blueprints": [
                BlueprintSerializer(self.blueprint_a).data,
                BlueprintSerializer(self.blueprint_b).data,
            ],
            "project": ProjectSerializer(self.project_base).data,
            "metadata": {"n_blueprints": 2, "n_participants": 2},
        }
        url = reverse("ddm_apis:project_overview", args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_donations_api_get_with_valid_api_credentials_specific_participant(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        expected_response = {
            "blueprints": {
                f"{self.blueprint_a.pk}": {
                    "blueprint_name": f"{self.blueprint_a.name}",
                    "donations": [
                        {
                            "participant": f"{self.participant_a.external_id}",
                            "data": ["data1_pA_bpA", "data2_pA_bpA"],
                            "time_submitted": f"{localtime(self.donation_pA_a.time_submitted).isoformat()}",  # noqa: E501
                            "data_extraction_state": f"{self.donation_pA_a.data_extraction_state}",  # noqa: E501
                            "consent": self.donation_pA_a.consent,
                            "n_data_entries": self.donation_pA_a.n_data_entries,
                        },
                    ],
                },
                f"{self.blueprint_b.pk}": {
                    "blueprint_name": f"{self.blueprint_b.name}",
                    "donations": [
                        {
                            "participant": f"{self.participant_a.external_id}",
                            "data": ["data1_pA_bpB", "data2_pA_bpB"],
                            "time_submitted": f"{localtime(self.donation_pA_b.time_submitted).isoformat()}",  # noqa: E501
                            "data_extraction_state": f"{self.donation_pA_b.data_extraction_state}",  # noqa: E501
                            "consent": self.donation_pA_b.consent,
                            "n_data_entries": self.donation_pA_b.n_data_entries,
                        },
                    ],
                },
            },
            "metadata": {"n_blueprints": 2},
        }

        url = (
            reverse("ddm_apis:donations", args=[self.project_base.url_id])
            + f"?participants={self.participant_a.external_id},nonsense"
        )
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_donations_api_get_with_valid_api_credentials_specific_blueprint(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        expected_response = {
            "blueprints": {
                f"{self.blueprint_a.pk}": {
                    "blueprint_name": f"{self.blueprint_a.name}",
                    "donations": [
                        {
                            "participant": f"{self.participant_a.external_id}",
                            "data": ["data1_pA_bpA", "data2_pA_bpA"],
                            "time_submitted": f"{localtime(self.donation_pA_a.time_submitted).isoformat()}",  # noqa: E501
                            "data_extraction_state": f"{self.donation_pA_a.data_extraction_state}",  # noqa: E501
                            "consent": self.donation_pA_a.consent,
                            "n_data_entries": self.donation_pA_a.n_data_entries,
                        },
                        {
                            "participant": f"{self.participant_b.external_id}",
                            "data": ["data1_pB_bpA", "data2_pB_bpA"],
                            "time_submitted": f"{localtime(self.donation_pB_a.time_submitted).isoformat()}",  # noqa: E501
                            "data_extraction_state": f"{self.donation_pB_a.data_extraction_state}",  # noqa: E501
                            "consent": self.donation_pB_a.consent,
                            "n_data_entries": self.donation_pB_a.n_data_entries,
                        },
                    ],
                },
            },
            "metadata": {"n_blueprints": 1},
        }
        url = reverse("ddm_apis:donations", args=[self.project_base.url_id])
        query_string = (
            f"?blueprints={self.blueprint_a.pk},123&"
            f"participants={self.participant_a.external_id},"
            f"{self.participant_b.external_id}"
        )
        response = client.get(url + query_string)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_donations_api_get_with_valid_api_credentials_no_participants_404(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse("ddm_apis:donations", args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_donations_api_get_fails_with_invalid_api_credentials(self):
        token = self.project_alt.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse("ddm_apis:donations", args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_donations_api_fails_with_no_api_credentials_created(self):
        token = self.project_base.create_token()
        key = token.key
        token.delete()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + key)
        url = reverse("ddm_apis:donations", args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_donations_api_returns_404_with_non_existing_project(self):
        token = self.project_base.create_token()
        key = token.key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + key)
        url = reverse("ddm_apis:donations", args=["non-existing-id"])
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_donations_api_returns_405_for_super_secret_project(self):
        token = self.project_super_secret.create_token()
        key = token.key
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + key)
        url = reverse("ddm_apis:donations", args=[self.project_super_secret.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 405)

    def _get_response_variable_name_context(self):
        return {
            "question_variable_names": {
                self.question_open.pk: self.question_open.variable_name
            },
            "item_variable_names": {},
        }

    def test_responses_api_get_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        context = self._get_response_variable_name_context()
        expected_response = {
            "responses": [
                ResponseSerializer(self.q_response_a, context=context).data,
                ResponseSerializer(self.q_response_b, context=context).data,
            ],
            "metadata": {
                "n_responses": len(self.project_base.questionnaireresponse_set.all())
            },
        }
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_responses_api_get_with_valid_api_credentials_and_snapshot(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        context = self._get_response_variable_name_context()
        expected_response = {
            "responses": [
                ResponseSerializerWithSnapshot(self.q_response_a, context=context).data,
                ResponseSerializerWithSnapshot(self.q_response_b, context=context).data,
            ],
            "metadata": {
                "n_responses": len(self.project_base.questionnaireresponse_set.all())
            },
        }
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        query_string = "?include_snapshot=true"
        response = client.get(url + query_string)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected_response)

    def test_responses_api_get_csv_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        query_string = "?csv=true"
        response = client.get(url + query_string)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_responses_api_get_csv_with_no_questionnaire(self):
        token = self.project_no_quest.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_no_quest.url_id])
        query_string = "?csv=true"
        response = client.get(url + query_string)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_responses_api_json_includes_is_complete(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        for entry in response.data["responses"]:
            self.assertIn("questionnaire_complete", entry)

    def test_responses_api_json_distinguishes_partial_responses(self):
        self.q_response_b.is_complete = False
        self.q_response_b.save()

        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        response = client.get(url)

        by_participant = {
            entry["participant"]: entry["questionnaire_complete"]
            for entry in response.data["responses"]
        }
        self.assertTrue(by_participant[self.participant_a.external_id])
        self.assertFalse(by_participant[self.participant_b.external_id])

        self.q_response_b.is_complete = True
        self.q_response_b.save()

    def test_responses_api_csv_includes_is_complete_column(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        response = client.get(url + "?csv=true")
        content = b"".join(response.streaming_content).decode()
        header = content.splitlines()[0]
        self.assertIn("questionnaire_complete", header)

    def test_participant_deletion_with_regular_login(self):
        self.client.login(**self.base_creds)

        new_participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now()
        )
        external_id = new_participant.external_id

        url = reverse(
            "ddm_apis:participant_delete", args=[self.project_base.url_id, external_id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Participant.objects.filter(external_id=external_id).first())

        url = reverse(
            "ddm_apis:participant_delete",
            args=[self.project_base.url_id, "nonsense_id"],
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_participant_deletion_fails_for_user_without_permission(self):
        self.client.login(**self.no_perm_creds)

        new_participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now()
        )
        external_id = new_participant.external_id

        url = reverse(
            "ddm_apis:participant_delete", args=[self.project_base.url_id, external_id]
        )
        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(
            Participant.objects.filter(external_id=external_id).first()
        )

    def test_participant_deletion_with_token(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        new_participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now()
        )
        external_id = new_participant.external_id

        url = reverse(
            "ddm_apis:participant_delete", args=[self.project_base.url_id, external_id]
        )
        response = client.delete(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Participant.objects.filter(external_id=external_id).first())

        url = reverse(
            "ddm_apis:participant_delete",
            args=[self.project_base.url_id, "some_bogus_id"],
        )
        response = client.delete(url)

        self.assertEqual(response.status_code, 404)

    def test_participant_deletion_fails_with_invalid_token(self):
        token = self.project_alt.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        new_participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now()
        )
        external_id = new_participant.external_id

        url = reverse(
            "ddm_apis:participant_delete", args=[self.project_base.url_id, external_id]
        )
        response = client.delete(url, follow=True)

        self.assertEqual(response.status_code, 401)
        self.assertIsNotNone(
            Participant.objects.filter(external_id=external_id).first()
        )

    def test_delete_project_data_with_regular_login_owner(self):
        self.client.login(**self.base_creds)
        url = reverse("ddm_apis:project_data_delete", args=[self.project_base.url_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_delete_project_data_fails_for_user_without_permission(self):
        self.client.login(**self.no_perm_creds)
        url = reverse("ddm_apis:project_data_delete", args=[self.project_base.url_id])
        response = self.client.delete(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_delete_project_data_fails_with_valid_api_credentials(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:project_data_delete", args=[self.project_base.url_id])
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(response.data)

    def test_delete_project_data_fails_with_invalid_api_credentials(self):
        token = self.project_alt.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:project_data_delete", args=[self.project_base.url_id])
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_project_data_with_no_api_credentials_created(self):
        token = self.project_base.create_token()
        key = token.key
        token.delete()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + key)
        url = reverse("ddm_apis:project_data_delete", args=[self.project_base.url_id])
        response = client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_download_project_detail_view_valid_login(self):
        self.client.login(**self.base_creds)
        url = reverse(
            "ddm_apis:download_project_details", args=[self.project_base.url_id]
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_download_project_detail_view_invalid_login(self):
        self.client.login(**self.no_perm_creds)
        url = reverse(
            "ddm_apis:download_project_details", args=[self.project_base.url_id]
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_download_project_detail_view_not_logged_in(self):
        client = Client()
        url = reverse(
            "ddm_apis:download_project_details", args=[self.project_base.url_id]
        )
        response = client.get(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_download_project_detail_view_csv_rows_match_header_length(self):
        """
        Regression test: participants that are missing a donation for a
        blueprint must still produce a row with the same number of columns
        as the header (previously, missing-donation blueprints emitted one
        fewer field than present ones, shifting all following columns).
        """
        participant_partial = Participant.objects.create(
            project=self.project_base, start_time=timezone.now()
        )
        DataDonation.objects.create(
            project=self.project_base,
            blueprint=self.blueprint_a,
            participant=participant_partial,
            time_submitted=timezone.now(),
            consent=True,
            data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
            n_data_entries=1,
            data=["data1_partial"],
        )
        # No donation created for blueprint_b for this participant.

        participant_none = Participant.objects.create(
            project=self.project_base, start_time=timezone.now()
        )
        # No donations at all for this participant.

        self.client.login(**self.base_creds)
        url = reverse(
            "ddm_apis:download_project_details", args=[self.project_base.url_id]
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        content = b"".join(response.streaming_content).decode()
        rows = list(csv.reader(io.StringIO(content)))
        header = rows[0]
        self.assertGreater(len(rows), 1)
        for row in rows[1:]:
            self.assertEqual(
                len(row),
                len(header),
                f"row {row!r} does not match header length {len(header)}",
            )

        by_participant = {row[0]: row for row in rows[1:]}
        partial_row = by_participant[participant_partial.external_id]
        # bp-<a>_name is populated, bp-<b>_name should be empty (no donation).
        bp_a_name_idx = header.index(f"bp-{self.blueprint_a.pk}_name")
        bp_b_name_idx = header.index(f"bp-{self.blueprint_b.pk}_name")
        self.assertEqual(partial_row[bp_a_name_idx], self.blueprint_a.name)
        self.assertEqual(partial_row[bp_b_name_idx], "")

        none_row = by_participant[participant_none.external_id]
        self.assertEqual(none_row[bp_a_name_idx], "")
        self.assertEqual(none_row[header.index("donation_download_link")], "")

    def test_download_project_detail_view_csv_escapes_special_characters(self):
        """A participant whose extra_data contains a comma/quote must not
        corrupt the CSV structure."""
        tricky_participant = Participant.objects.create(
            project=self.project_base,
            start_time=timezone.now(),
            extra_data={"note": 'contains, a comma and "quotes"'},
        )

        self.client.login(**self.base_creds)
        url = reverse(
            "ddm_apis:download_project_details", args=[self.project_base.url_id]
        )
        response = self.client.get(url, follow=True)
        content = b"".join(response.streaming_content).decode()
        rows = list(csv.reader(io.StringIO(content)))
        header = rows[0]

        by_participant = {row[0]: row for row in rows[1:]}
        row = by_participant[tricky_participant.external_id]
        self.assertEqual(len(row), len(header))
        self.assertIn("contains, a comma", row[header.index("extra_data")])

    def test_download_project_detail_view_query_count_is_constant(self):
        """
        The number of queries used to build the CSV should not scale with
        the number of participants/blueprints (regression test for the
        N+1 query bug in get_blueprint_donation_data).
        """
        self.client.login(**self.base_creds)
        url = reverse(
            "ddm_apis:download_project_details", args=[self.project_base.url_id]
        )

        with CaptureQueriesContext(connection) as small_ctx:
            response = self.client.get(url, follow=True)
            b"".join(response.streaming_content)

        for _ in range(20):
            participant = Participant.objects.create(
                project=self.project_base, start_time=timezone.now()
            )
            DataDonation.objects.create(
                project=self.project_base,
                blueprint=self.blueprint_a,
                participant=participant,
                time_submitted=timezone.now(),
                consent=True,
                data_extraction_state=DataDonation.DataExtractionState.DATA_EXTRACTED,
                n_data_entries=1,
                data=["extra"],
            )

        with CaptureQueriesContext(connection) as large_ctx:
            response = self.client.get(url, follow=True)
            b"".join(response.streaming_content)

        # Query count should stay (roughly) flat, not grow with the number
        # of newly added participants/donations.
        small_count = len(small_ctx.captured_queries)
        large_count = len(large_ctx.captured_queries)
        self.assertLess(large_count, small_count + 5)

    def test_responses_api_resolves_new_format_response_data(self):
        """
        Regression test for the get_response_data N+1 fix: responses saved in
        the current ("question-<id>"/"item-<id>" prefixed) format must still
        resolve to the correct variable names via the context-based lookup.
        """
        question = MultiChoiceQuestion.objects.create(
            project=self.project_base,
            name="multi question",
            page=1,
            index=2,
            variable_name="multi",
        )
        item_1 = QuestionItem.objects.create(question=question, index=1, value=1)
        item_2 = QuestionItem.objects.create(question=question, index=2, value=2)

        participant = Participant.objects.create(
            project=self.project_base, start_time=timezone.now()
        )
        response_data = {
            f"question-{question.pk}": "not applicable",
            f"item-{item_1.pk}": 1,
            f"item-{item_2.pk}": 0,
        }
        QuestionnaireResponse.objects.create(
            project=self.project_base,
            participant=participant,
            time_submitted=timezone.now(),
            data=json.dumps(response_data),
        )

        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        response = client.get(url + f"?participants={participant.external_id}")

        self.assertEqual(response.status_code, 200)
        resolved = response.data["responses"][0]["response_data"]
        self.assertEqual(resolved["multi-1"], 1)
        self.assertEqual(resolved["multi-2"], 0)
        self.assertNotIn(f"question-{question.pk}", resolved)
        self.assertNotIn(f"item-{item_1.pk}", resolved)

    def test_responses_api_query_count_is_constant(self):
        """
        Regression test: neither the JSON nor the CSV response export should
        issue more queries as the number of responses/questions/items grows.
        """
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])

        with CaptureQueriesContext(connection) as small_json_ctx:
            self.assertEqual(client.get(url).status_code, 200)
        with CaptureQueriesContext(connection) as small_csv_ctx:
            response = client.get(url + "?csv=true")
            b"".join(response.streaming_content)

        for i in range(10):
            question = MultiChoiceQuestion.objects.create(
                project=self.project_base,
                name=f"multi question {i}",
                page=1,
                index=10 + i,
                variable_name=f"multi_{i}",
            )
            item = QuestionItem.objects.create(question=question, index=1, value=1)
            participant = Participant.objects.create(
                project=self.project_base, start_time=timezone.now()
            )
            QuestionnaireResponse.objects.create(
                project=self.project_base,
                participant=participant,
                time_submitted=timezone.now(),
                data=json.dumps(
                    {f"question-{question.pk}": "value", f"item-{item.pk}": 1}
                ),
            )

        with CaptureQueriesContext(connection) as large_json_ctx:
            self.assertEqual(client.get(url).status_code, 200)
        with CaptureQueriesContext(connection) as large_csv_ctx:
            response = client.get(url + "?csv=true")
            self.assertEqual(response.status_code, 200)
            b"".join(response.streaming_content)

        self.assertLess(
            len(large_json_ctx.captured_queries),
            len(small_json_ctx.captured_queries) + 5,
        )
        self.assertLess(
            len(large_csv_ctx.captured_queries),
            len(small_csv_ctx.captured_queries) + 5,
        )

    def test_responses_api_snapshot_and_response_data_both_correct(self):
        """
        Regression test for the decrypted-data caching fix: requesting both
        response_data and questionnaire_snapshot (via include_snapshot=true)
        for the same response must not corrupt or drop either field.
        """
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        response = client.get(
            url
            + f"?participants={self.participant_a.external_id}&include_snapshot=true"
        )
        self.assertEqual(response.status_code, 200)
        entry = response.data["responses"][0]
        self.assertIn("questionnaire_snapshot", entry)
        self.assertEqual(entry["response_data"]["open"], "response_data")

    def test_responses_api_csv_uses_resolved_variable_names(self):
        token = self.project_base.create_token()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse("ddm_apis:responses", args=[self.project_base.url_id])
        response = client.get(url + "?csv=true")
        content = b"".join(response.streaming_content).decode()
        rows = list(csv.reader(io.StringIO(content)))
        header = rows[0]
        self.assertIn("open", header)
        self.assertNotIn(str(self.question_open.pk), header)
        for row in rows[1:]:
            self.assertEqual(len(row), len(header))
