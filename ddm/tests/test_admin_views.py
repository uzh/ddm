from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from ddm.models import (
    DonationProject, DonationBlueprint, OpenQuestion, ZippedBlueprint,
    SingleChoiceQuestion, MatrixQuestion, DonationInstruction, ResearchProfile
)


test_settings = {'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', }


class BaseTestCaseAdminViews:
    @classmethod
    def setUpTestData(cls):
        cls.test_user_credentials = {
            'username': 'test_user', 'password': '123', 'email': 'u2@mail.com'}
        cls.test_user = User.objects.create_user(**cls.test_user_credentials)
        cls.test_user_profile = ResearchProfile.objects.create(user=cls.test_user)
        DonationProject.objects.create(
            name='Project 1', slug='project-1', owner=cls.test_user_profile)

        cls.mock_user_credentials = {
            'username': 'mock_user', 'password': '123', 'email': 'u3@mail.com'}
        cls.mock_user = User.objects.create_user(**cls.mock_user_credentials)
        mock_user_profile = ResearchProfile.objects.create(user=cls.mock_user)
        DonationProject.objects.create(
            name='Project 2', slug='project-2', owner=mock_user_profile)

        cls.user_without_profile_credentials = {
            'username': 'no_profile_user', 'password': '123', 'email': 'noprof@mail.com'}
        cls.user_without_profile = User.objects.create_user(
            **cls.user_without_profile_credentials)

        cls.user_without_permission_credentials = {
            'username': 'no_permission_user', 'password': '123', 'email': 'noperm@liam.com'}
        cls.user_without_permission = User.objects.create_user(
            **cls.user_without_permission_credentials)
        no_permission_profile = ResearchProfile.objects.create(
            user=cls.user_without_permission)
        cls.project_without_permission = DonationProject.objects.create(
            name='Project 3', slug='project-3', owner=no_permission_profile)

        cls.project = DonationProject.objects.create(
            name='Test Project',
            slug='test-project',
            owner=cls.test_user_profile
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
        User.objects.create_superuser(cls.user_name, 'test@mail.com', cls.user_pw)

    def test_logged_out_redirects_to_login_view(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('ddm-login'))

    def test_superuser_logged_in_returns_200(self):
        self.client.login(username=self.user_name, password=self.user_pw)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_owner_logged_in_returns_200(self):
        self.client.login(**self.test_user_credentials)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_non_owner_logged_in_returns_404(self):
        if self.url in [reverse('project-list'), reverse('project-create')]:
            pass
        else:
            self.client.login(**self.mock_user_credentials)
            response = self.client.get(self.url, follow=True)
            self.assertEqual(response.status_code, 404)

    def test_user_without_profile_logged_in_redirects_to_registration_view(self):
        self.client.login(**self.user_without_profile_credentials)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('ddm-register'))

    def test_user_without_permission_logged_in_redirects_to_no_permission_view(self):
        if self.url in [reverse('project-list'), reverse('project-create')]:
            pass
        else:
            self.client.login(**self.user_without_permission_credentials)
            response = self.client.get(self.url_no_permission, follow=True)
            self.assertRedirects(response, reverse('ddm-no-permission'))


@override_settings(DDM_SETTINGS=test_settings)
class ProjectListViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-list', args=[])

    def test_correct_queryset_returned(self):
        self.client.login(**self.test_user_credentials)
        response = self.client.get(reverse('project-list'))
        object_list = response.context['object_list']
        expected_queryset = DonationProject.objects.filter(owner__user=self.test_user)
        self.assertQuerysetEqual(object_list, list(expected_queryset), ordered=False)


@override_settings(DDM_SETTINGS=test_settings)
class ProjectCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-create', args=[])

    def test_project_is_created(self):
        self.client.login(**self.test_user_credentials)
        self.client.post(
            reverse('project-create'),
            data={'name': 'new-test-project', 'slug': 'new_slug'}
        )
        self.assertTrue(DonationProject.objects.filter(owner__user=self.test_user, slug='new_slug').exists())


@override_settings(DDM_SETTINGS=test_settings)
class ProjectEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-edit', args=[self.project.pk])
        self.url_no_permission = reverse(
            'project-edit',
            args=[self.project_without_permission.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class ProjectDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-delete', args=[self.project.pk])
        self.url_no_permission = reverse(
            'project-delete',
            args=[self.project_without_permission.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class ProjectWelcomeEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('welcome-page-edit', args=[self.project.pk])
        self.url_no_permission = reverse(
            'welcome-page-edit',
            args=[self.project_without_permission.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class ProjectEndEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('end-page-edit', args=[self.project.pk])
        self.url_no_permission = reverse(
            'end-page-edit',
            args=[self.project_without_permission.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class BlueprintListViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-list', args=[self.project.pk])
        self.url_no_permission = reverse(
            'blueprint-list',
            args=[self.project_without_permission.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class BlueprintCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'blueprint-create',
            args=[self.project.pk]
        )
        self.url_no_permission = reverse(
            'blueprint-create',
            args=[self.project_without_permission.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class BlueprintEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'blueprint-edit',
            args=[self.project.pk, self.dbp.pk]
        )
        self.url_no_permission = reverse(
            'blueprint-edit',
            args=[self.project_without_permission.pk, self.dbp.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class BlueprintDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'blueprint-delete',
            args=[self.project.pk, self.dbp.pk]
        )
        self.url_no_permission = reverse(
            'blueprint-delete',
            args=[self.project_without_permission.pk, self.dbp.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class ZippedBlueprintCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'zipped-blueprint-create',
            args=[self.project.pk]
        )
        self.url_no_permission = reverse(
            'zipped-blueprint-create',
            args=[self.project_without_permission.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class ZippedBlueprintEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'zipped-blueprint-edit',
            args=[self.project.pk, self.zbp.pk]
        )
        self.url_no_permission = reverse(
            'zipped-blueprint-edit',
            args=[self.project_without_permission.pk, self.zbp.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class ZippedBlueprintDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('zipped-blueprint-delete', args=[self.project.pk, self.zbp.pk])
        self.url_no_permission = reverse(
            'zipped-blueprint-delete',
            args=[self.project_without_permission.pk, self.zbp.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class InstructionListViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'instruction-overview',
            args=[self.project.pk, 'blueprint', self.dbp.pk]
        )
        self.url_no_permission = reverse(
            'instruction-overview',
            args=[self.project_without_permission.pk, 'blueprint', self.dbp.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class InstructionCreateViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'instruction-create',
            args=[self.project.pk, 'blueprint', self.dbp.pk]
        )
        self.url_no_permission = reverse(
            'instruction-create',
            args=[self.project_without_permission.pk, 'blueprint', self.dbp.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class InstructionEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'instruction-edit',
            args=[self.project.pk, 'blueprint', self.dbp.pk, self.instruction.pk]
        )
        self.url_no_permission = reverse(
            'instruction-edit',
            args=[self.project_without_permission.pk, 'blueprint', self.dbp.pk, self.instruction.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class InstructionDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'instruction-delete',
            args=[self.project.pk, 'blueprint', self.dbp.pk, self.instruction.pk]
        )
        self.url_no_permission = reverse(
            'instruction-delete',
            args=[self.project_without_permission.pk, 'blueprint', self.dbp.pk, self.instruction.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class QuestionnaireOverviewViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('questionnaire-overview',  args=[self.project.pk])
        self.url_no_permission = reverse(
            'questionnaire-overview',
            args=[self.project_without_permission.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
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

    def test_logged_out_redirects_to_login_view(self):
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('ddm-login'))

    def test_superuser_logged_in_returns_200(self):
        self.client.login(username=self.user_name, password=self.user_pw)
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_owner_logged_in_returns_200(self):
        self.client.login(**self.test_user_credentials)
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_non_owner_logged_in_returns_404(self):
        self.client.login(**self.mock_user_credentials)
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 404)

    def test_user_without_profile_logged_in_redirects_to_registration_view(self):
        self.client.login(**self.user_without_profile_credentials)
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('ddm-register'))

    def test_user_without_permission_logged_in_redirects_to_no_permission_view(self):
        self.client.login(**self.user_without_permission_credentials)
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project_without_permission.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('ddm-no-permission'))


@override_settings(DDM_SETTINGS=test_settings)
class QuestionEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'question-edit',
            args=[self.project.pk, 'open', self.open_question.pk]
        )
        self.url_no_permission = reverse(
            'question-edit',
            args=[self.project_without_permission.pk, 'open', self.open_question.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class QuestionDeleteViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'question-delete',
            args=[self.project.pk, 'open', self.open_question.pk]
        )
        self.url_no_permission = reverse(
            'question-delete',
            args=[self.project_without_permission.pk, 'open', self.open_question.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class QuestionItemsEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'question-items',
            args=[self.project.pk, 'single_choice', self.sc_question.pk]
        )
        self.url_no_permission = reverse(
            'question-items',
            args=[self.project_without_permission.pk, 'single_choice', self.sc_question.pk]
        )


@override_settings(DDM_SETTINGS=test_settings)
class QuestionScaleEditViewTests(BaseTestCaseAdminViews, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse(
            'question-scale',
            args=[self.project.pk, 'matrix', self.matrix_question.pk]
        )
        self.url_no_permission = reverse(
            'question-scale',
            args=[self.project_without_permission.pk, 'matrix', self.matrix_question.pk]
        )
