from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from ddm.models import (
    DonationProject, DonationBlueprint, OpenQuestion, ZippedBlueprint,
    SingleChoiceQuestion, MatrixQuestion, DonationInstruction
)


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
