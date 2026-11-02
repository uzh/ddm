from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from ddm.datadonation.models import DonationBlueprint, FileUploader
from ddm.datadonation.schemas import JSONParserConfig
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import OpenQuestion

User = get_user_model()


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestQuestionnaireOverview(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=cls.user)

        cls.project = DonationProject.objects.create(
            name="Base Project", slug="base", owner=profile
        )

        cls.file_uploader = FileUploader.objects.create(
            project=cls.project,
            name="basic file uploader",
            upload_type=FileUploader.UploadTypes.ZIP_FILE,
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project,
            name="blueprint",
            display_name="blueprint",
            description="some description",
            expected_fields='"some field"',
            file_uploader=cls.file_uploader,
            parser_config=JSONParserConfig().model_dump(),
        )

        cls.url = reverse(
            "ddm_questionnaire:overview", kwargs={"project_url_id": cls.project.url_id}
        )

        for page in (1, 2):
            for index in (1, 2):
                OpenQuestion.objects.create(
                    project=cls.project,
                    blueprint=cls.blueprint,
                    name=f"question p{page}i{index}",
                    variable_name=f"question_p{page}i{index}",
                    page=page,
                    index=index,
                )

    def test_groups_questions_by_page_and_resolves_blueprint(self):
        self.client.login(username="owner", password="123")
        response = self.client.get(self.url)
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("question p1i1", content)
        self.assertIn("question p2i2", content)
        self.assertIn(self.blueprint.name, content)

    def test_query_count_is_constant_regardless_of_question_count(self):
        """The number of queries used to render the page should not scale with the
        number of pages/questions in the questionnaire."""
        self.client.login(username="owner", password="123")

        with CaptureQueriesContext(connection) as small_ctx:
            self.client.get(self.url)

        for page in range(3, 13):
            for index in (1, 2, 3):
                OpenQuestion.objects.create(
                    project=self.project,
                    blueprint=self.blueprint,
                    name=f"question p{page}i{index}",
                    variable_name=f"question_p{page}i{index}",
                    page=page,
                    index=index,
                )

        with CaptureQueriesContext(connection) as large_ctx:
            self.client.get(self.url)

        small_count = len(small_ctx.captured_queries)
        large_count = len(large_ctx.captured_queries)
        self.assertLess(large_count, small_count + 5)
