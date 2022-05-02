from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from ddm.models import (
    DonationProject, DonationBlueprint, OpenQuestion, DataDonation, Participant,
    ZippedBlueprint, SingleChoiceQuestion, MatrixQuestion, DonationInstruction
)


class BaseViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Project with associated data donation and questions:
        cls.project = DonationProject.objects.create(
            name='Test Project',
            slug='test-project'
        )
        cls.dbp = DonationBlueprint.objects.create(
            project=cls.project,
            name='donation blueprint',
            expected_fields='a,b',
            extracted_fields='a'
        )
        OpenQuestion.objects.create(
            project=cls.project,
            blueprint=cls.dbp,
            name='a question',
            variable_name='a_question'
        )
        # Project without associated data donation and questions:
        cls.project_no = DonationProject.objects.create(
            name='Test Project without Questionnaire',
            slug='test-project-without'
        )

    def setUp(self):
        # URLs for project with questionnaire.
        self.entry_url = reverse('project-entry', args=[self.project.slug])
        self.dd_url = reverse('data-donation', args=[self.project.slug])
        self.quest_url = reverse('questionnaire', args=[self.project.slug])
        self.exit_url = reverse('project-exit', args=[self.project.slug])

        # URLs for project without questionnaire.
        self.entry_url_no = reverse('project-entry', args=[self.project_no.slug])
        self.dd_url_no = reverse('data-donation', args=[self.project_no.slug])
        self.quest_url_no = reverse('questionnaire', args=[self.project_no.slug])
        self.exit_url_no = reverse('project-exit', args=[self.project_no.slug])

        # URLs for non-existing project.
        self.entry_url_bad = reverse('project-entry', args=['nope'])
        self.dd_url_bad = reverse('data-donation', args=['nope'])
        self.quest_url_bad = reverse('questionnaire', args=['nope'])
        self.exit_url_bad = reverse('project-exit', args=['nope'])

        # Initialize client and add projects to session.
        self.client = Client()
        self.client.get(self.entry_url)
        self.client.get(self.entry_url_no)

        # Create a data donation for project 1.
        participant_id = self.client.session['projects'][f'{self.project.pk}']['participant_id']
        participant = Participant.objects.get(pk=int(participant_id))
        DataDonation.objects.create(
            project=self.project,
            blueprint=self.dbp,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data='{}'
        )


class TestEntryView(BaseViewsTestCase):

    def setUp(self):
        super().setUp()

    def test_project_entry_GET(self):
        good_response = self.client.get(self.entry_url)
        bad_response = self.client.get(self.entry_url_bad)

        self.assertEqual(good_response.status_code, 200)
        self.assertEqual(bad_response.status_code, 404)
        self.assertTemplateUsed(good_response, 'ddm/public/entry_page.html')

    def test_project_entry_POST(self):
        response = self.client.post(self.entry_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dd_url)


class TestDonationView(BaseViewsTestCase):

    def setUp(self):
        super().setUp()

        session = self.client.session
        session['projects'][f'{self.project.pk}']['steps']['project-entry']['state'] = 'completed'
        session.save()

    def test_data_donation_GET(self):
        good_response = self.client.get(self.dd_url)
        bad_response = self.client.get(self.dd_url_bad)

        self.assertEqual(good_response.status_code, 200)
        self.assertEqual(bad_response.status_code, 404)
        self.assertTemplateUsed(good_response, 'ddm/public/data_donation.html')

    def test_data_donation_POST_redirect(self):
        response = self.client.post(self.dd_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.quest_url)


class TestQuestionnaireView(BaseViewsTestCase):

    def setUp(self):
        super().setUp()

        # Manipulate sessions.
        session = self.client.session
        session['projects'][f'{self.project.pk}']['steps']['project-entry']['state'] = 'completed'
        session['projects'][f'{self.project.pk}']['steps']['data-donation']['state'] = 'completed'
        session['projects'][f'{self.project_no.pk}']['steps']['project-entry']['state'] = 'completed'
        session['projects'][f'{self.project_no.pk}']['steps']['data-donation']['state'] = 'completed'
        session.save()

    def test_questionnaire_GET_questionnaire_defined(self):
        good_response = self.client.get(self.quest_url)
        bad_response = self.client.get(self.quest_url_bad)

        self.assertEqual(good_response.status_code, 200)
        self.assertEqual(bad_response.status_code, 404)
        self.assertTemplateUsed(good_response, 'ddm/public/questionnaire.html')

    def test_questionnaire_GET_no_questionnaire(self):
        good_response = self.client.get(self.quest_url_no)
        self.assertRedirects(good_response, self.exit_url_no)

    def test_questionnaire_POST_redirect(self):
        response = self.client.post(self.quest_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.exit_url)


class TestExitView(BaseViewsTestCase):

    def setUp(self):
        super().setUp()

        session = self.client.session
        session['projects'][f'{self.project.pk}']['steps']['project-entry']['state'] = 'completed'
        session['projects'][f'{self.project.pk}']['steps']['data-donation']['state'] = 'completed'
        session['projects'][f'{self.project.pk}']['steps']['questionnaire']['state'] = 'completed'
        session.save()

    def test_project_exit_GET(self):
        good_response = self.client.get(self.exit_url)
        bad_response = self.client.get(self.exit_url_bad)

        self.assertEqual(good_response.status_code, 200)
        self.assertEqual(bad_response.status_code, 404)
        self.assertTemplateUsed(good_response, 'ddm/public/end.html')

    def test_project_exit_POST(self):
        response = self.client.post(self.exit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/end.html')


class BaseTestCaseAdminViews:
    @classmethod
    def setUpTestData(cls):
        cls.project = DonationProject.objects.create(
            name='Test Project',
            slug='test-project'
        )
        cls.dbp = DonationBlueprint.objects.create(
            project=cls.project,
            name='donation blueprint',
            expected_fields='a,b',
            extracted_fields='a'
        )
        cls.zbp = ZippedBlueprint.objects.create(
            name='zipped blueprint',
            project=cls.project
        )
        cls.open_question = OpenQuestion.objects.create(
            project=cls.project,
            blueprint=cls.dbp,
            name='open question',
            variable_name='open_question'
        )
        cls.sc_question = SingleChoiceQuestion.objects.create(
            project=cls.project,
            blueprint=cls.dbp,
            name='sc question',
            variable_name='sc_question'
        )
        cls.matrix_question = MatrixQuestion.objects.create(
            project=cls.project,
            blueprint=cls.dbp,
            name='matrix question',
            variable_name='matrix_question'
        )
        cls.instruction = DonationInstruction.objects.create(
            text='some text',
            index=1,
            blueprint=cls.dbp
        )
        cls.user_name = 'test-user'
        cls.user_pw = 'test-password'
        User.objects.create_superuser(cls.user_name, 'test@test.com', cls.user_pw)

    def setUp(self):
        self.client = Client()

    def test_logged_in_returns_200(self):
        self.client.login(username=self.user_name, password=self.user_pw)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_logged_out_returns_404(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)


class ProjectListViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-list', args=[])


class ProjectCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-create', args=[])


class ProjectEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-edit', args=[self.project.pk])


class ProjectDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-delete', args=[self.project.pk])


class ProjectWelcomeEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('welcome-page-edit', args=[self.project.pk])


class ProjectEndEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('end-page-edit', args=[self.project.pk])


class BlueprintListViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-list', args=[self.project.pk])


class BlueprintCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-create', args=[self.project.pk])


class BlueprintEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-edit', args=[self.project.pk, self.dbp.pk])


class BlueprintDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-delete', args=[self.project.pk, self.dbp.pk])


class ZippedBlueprintCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('zipped-blueprint-create', args=[self.project.pk])


class ZippedBlueprintEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('zipped-blueprint-edit', args=[self.project.pk, self.zbp.pk])


class ZippedBlueprintDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('zipped-blueprint-delete', args=[self.project.pk, self.zbp.pk])


class InstructionListViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'instruction-overview',
            args=[self.project.pk, 'blueprint', self.dbp.pk]
        )


class InstructionCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'instruction-create',
            args=[self.project.pk, 'blueprint', self.dbp.pk]
        )


class InstructionEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'instruction-edit',
            args=[self.project.pk, 'blueprint', self.dbp.pk, self.instruction.pk]
        )


class InstructionDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'instruction-delete',
            args=[self.project.pk, 'blueprint', self.dbp.pk, self.instruction.pk]
        )


class QuestionnaireOverviewViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('questionnaire-overview',  args=[self.project.pk])


class QuestionCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.question_type_slugs = [
            'single_choice',
            'multi_choice',
            'open',
            'matrix',
            'semantic_diff',
            'transition'
        ]

    def test_logged_in_returns_200(self):
        self.client.login(username=self.user_name, password=self.user_pw)
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project.pk, slug])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_logged_out_returns_404(self):
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 404)


class QuestionEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'question-edit',
            args=[self.project.pk, 'open', self.open_question.pk]
        )


class QuestionDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'question-delete',
            args=[self.project.pk, 'open', self.open_question.pk]
        )


class QuestionItemsEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'question-items',
            args=[self.project.pk, 'single_choice', self.sc_question.pk]
        )


class QuestionScaleEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'question-scale',
            args=[self.project.pk, 'matrix', self.matrix_question.pk]
        )


# TODO: Add Class TestViewsRerouting(TestCase)
