# ruff: noqa: T201, TRY201, N812
import os
import unittest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from ddm.datadonation.models import DonationBlueprint, DonationInstruction, FileUploader
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.questionnaire.models import QuestionItem, SingleChoiceQuestion

User = get_user_model()


@unittest.skipUnless(
    os.environ.get("RUN_INTEGRATION_TESTS"),
    "Skipping integration tests. Set RUN_INTEGRATION_TESTS=1 to run.",
)
class TestDDMUploaderIntegration(StaticLiveServerTestCase):
    """Minimal integration test of the vue uploader component.

    Not run as part of the main testing suite.
    To run, use:
    - Linux/Mac: RUN_INTEGRATION_TESTS=1 python manage.py \
        test ddm.participation.tests.test_frontend_integration
    - Win Powershell: $env:RUN_INTEGRATION_TESTS=1; python manage.py \
        test ddm.participation.tests.test_frontend_integration

    Afterward run:
    - Linux/Mac: unset RUN_INTEGRATION_TESTS
    - Win Powershell: $env:RUN_INTEGRATION_TESTS = $null
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,4000")

        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        user = User.objects.create_user(
            username="owner", password="123", email="owner@mail.com"
        )
        profile = ResearchProfile.objects.create(user=user)

        self.project = DonationProject.objects.create(
            name="Base Project",
            slug="base",
            owner=profile,
            custom_uploader_translations={
                "en": {"instructions": {"heading": "custom heading"}},
                "de": {"instructions": {"heading": "custom heading"}},
            },
        )

        file_uploader = FileUploader.objects.create(
            project=self.project,
            name="basic_file_uploader",
            display_name="basic file uploader",
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
        )

        DonationInstruction.objects.create(
            file_uploader=file_uploader,
            text="some instructions",
            index=1,
        )

        self.blueprint = DonationBlueprint.objects.create(
            project=self.project,
            name="donation_blueprint",
            display_name="donation blueprint",
            description="blueprint description",
            expected_fields='"a", "b"',
            file_uploader=file_uploader,
        )

        self.sc_question = SingleChoiceQuestion.objects.create(
            project=self.project,
            name="open question",
            variable_name="open_question",
            text="open question text",
        )

        self.sc_item = QuestionItem.objects.create(
            question=self.sc_question,
            index=1,
            label="label sc item",
            value=1,
        )

        # URLs
        project_slug = self.project.slug
        self.briefing_url = reverse("ddm_participation:briefing", args=[project_slug])
        self.dd_url = reverse("ddm_participation:datadonation", args=[project_slug])
        self.quest_url = reverse("ddm_participation:questionnaire", args=[project_slug])
        self.debriefing_url = reverse(
            "ddm_participation:debriefing", args=[project_slug]
        )

    def _initialize_session_and_get_participant(self):
        """Visit briefing to create session, then return participant."""
        briefing_url = f"{self.live_server_url}/studies/base/briefing/"
        self.driver.get(briefing_url)

        # Debug: print cookies
        cookies = self.driver.get_cookies()
        print(f"Cookies after briefing: {cookies}")

        # Check if session cookie exists
        session_cookie = self.driver.get_cookie(settings.SESSION_COOKIE_NAME)

        session_id = session_cookie["value"]
        session = Session.objects.get(session_key=session_id)
        session_data = session.get_decoded()

        print(f"Session data: {session_data}")

        participant_id = session_data[f"project-{self.project.pk}"]["participant_id"]
        return Participant.objects.get(pk=int(participant_id))

    def test_vue_uploader_component_renders(self):
        participant = self._initialize_session_and_get_participant()
        participant.current_step = 1
        participant.save()

        donation_url = f"{self.live_server_url}/studies/base/data-donation/"
        self.driver.get(donation_url)

        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.all_of(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".uploader-container")
                    ),
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, "#uapp"), self.blueprint.display_name
                    ),
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, "#uapp"), self.blueprint.description
                    ),
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, "#uapp"), "custom heading"
                    ),
                )
            )
            self.assertIsNotNone(element)
        except Exception as e:
            self._save_debug_screenshot("uploader")
            raise e

    def test_vue_questionnaire_component_renders(self):
        participant = self._initialize_session_and_get_participant()
        participant.current_step = 2
        participant.save()

        questionnaire_url = f"{self.live_server_url}/studies/base/questionnaire/"
        self.driver.get(questionnaire_url)

        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.all_of(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".question-app-container")
                    ),
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, "#qapp"), self.sc_question.text
                    ),
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, "#qapp"), self.sc_item.label
                    ),
                )
            )
            self.assertIsNotNone(element)
        except Exception as e:
            self._save_debug_screenshot("questionnaire")
            raise e

    def _save_debug_screenshot(self, name):
        now = timezone.now()
        filename = f"test_failure_{name}_{now:%Y%m%d_%H%M%S}.png"
        self.driver.save_screenshot(filename)
        print(f"Screenshot saved: {filename}")
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page source: {self.driver.page_source[:1000]}")
