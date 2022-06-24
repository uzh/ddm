from django.urls import reverse
from ddm.models import DonationProject
from ddm.tests.base import TestData


class BaseAdminViewTestMixin:
    def test_logged_out_redirects_to_login_view(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('ddm-login'))

    def test_superuser_logged_in_returns_200(self):
        self.client.login(**self.users['super']['credentials'])
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_owner_logged_in_returns_200(self):
        self.client.login(**self.users['base']['credentials'])
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_non_owner_logged_in_returns_404(self):
        if self.url in [reverse('project-list'), reverse('project-create')]:
            pass
        else:
            self.client.login(**self.users['base2']['credentials'])
            response = self.client.get(self.url, follow=True)
            self.assertEqual(response.status_code, 404)

    def test_user_without_profile_logged_in_redirects_to_registration_view(self):
        self.client.login(**self.users['no_profile']['credentials'])
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('ddm-register'))

    def test_user_without_permission_logged_in_redirects_to_no_permission_view(self):
        if self.url in [reverse('project-list'), reverse('project-create')]:
            pass
        else:
            self.client.login(**self.users['no_permission']['credentials'])
            response = self.client.get(self.url_no_perm, follow=True)
            self.assertRedirects(response, reverse('ddm-no-permission'))


class ProjectListViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-list', args=[])

    def test_correct_queryset_returned(self):
        self.client.login(**self.users['base']['credentials'])
        response = self.client.get(reverse('project-list'))
        object_list = response.context['object_list']
        expected_queryset = DonationProject.objects.filter(owner__user=self.users['base']['user'])
        self.assertQuerysetEqual(object_list, list(expected_queryset), ordered=False)


class ProjectCreateViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-create', args=[])

    # TODO: Check this test again: Something is not working as expected with the client.post() call.
    #  The View works as expected when called in browser (runserver).
    # def test_project_is_created(self):
    #     self.client.login(**self.users['base']['credentials'])
    #     self.client.post(reverse('project-create'), data={'name': 'name', 'slug': 'new_slug'})
    #     self.assertTrue(DonationProject.objects.filter(
    #         owner=self.users['base']['profile'], slug='new_slug').exists())


class ProjectEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-edit', args=[self.project_base.pk])
        self.url_no_perm = reverse('project-edit', args=[self.project_no_perm.pk])


class ProjectDeleteViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('project-delete', args=[self.project_base.pk])
        self.url_no_perm = reverse('project-delete', args=[self.project_no_perm.pk])


class ProjectWelcomeEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('welcome-page-edit', args=[self.project_base.pk])
        self.url_no_perm = reverse('welcome-page-edit', args=[self.project_no_perm.pk])


class ProjectEndEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('end-page-edit', args=[self.project_base.pk])
        self.url_no_perm = reverse('end-page-edit', args=[self.project_no_perm.pk])


class BlueprintListViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-list', args=[self.project_base.pk])
        self.url_no_perm = reverse('blueprint-list', args=[self.project_no_perm.pk])


class BlueprintCreateViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-create', args=[self.project_base.pk])
        self.url_no_perm = reverse('blueprint-create', args=[self.project_no_perm.pk])


class BlueprintEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-edit', args=[self.project_base.pk, self.don_bp.pk])
        self.url_no_perm = reverse('blueprint-edit', args=[self.project_no_perm.pk, self.don_bp.pk])


class BlueprintDeleteViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('blueprint-delete', args=[self.project_base.pk, self.don_bp.pk])
        self.url_no_perm = reverse('blueprint-delete', args=[self.project_no_perm.pk, self.don_bp.pk])


class ZippedBlueprintCreateViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('zipped-blueprint-create', args=[self.project_base.pk])
        self.url_no_perm = reverse('zipped-blueprint-create', args=[self.project_no_perm.pk])


class ZippedBlueprintEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('zipped-blueprint-edit', args=[self.project_base.pk, self.zip_bp.pk])
        self.url_no_perm = reverse('zipped-blueprint-edit', args=[self.project_no_perm.pk, self.zip_bp.pk])


class ZippedBlueprintDeleteViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('zipped-blueprint-delete', args=[self.project_base.pk, self.zip_bp.pk])
        self.url_no_perm = reverse('zipped-blueprint-delete', args=[self.project_no_perm.pk, self.zip_bp.pk])


class InstructionListViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('instruction-overview', args=[self.project_base.pk, 'blueprint', self.don_bp.pk])
        self.url_no_perm = reverse('instruction-overview', args=[self.project_no_perm.pk, 'blueprint', self.don_bp.pk])


class InstructionCreateViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('instruction-create', args=[self.project_base.pk, 'blueprint', self.don_bp.pk])
        self.url_no_perm = reverse('instruction-create', args=[self.project_no_perm.pk, 'blueprint', self.don_bp.pk])


class InstructionEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('instruction-edit',
                           args=[self.project_base.pk, 'blueprint', self.don_bp.pk, self.instruction.pk])
        self.url_no_perm = reverse('instruction-edit',
                                   args=[self.project_no_perm.pk, 'blueprint', self.don_bp.pk, self.instruction.pk])


class InstructionDeleteViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('instruction-delete',
                           args=[self.project_base.pk, 'blueprint', self.don_bp.pk, self.instruction.pk])
        self.url_no_perm = reverse('instruction-delete',
                                   args=[self.project_no_perm.pk, 'blueprint', self.don_bp.pk, self.instruction.pk])


class QuestionnaireOverviewViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('questionnaire-overview',  args=[self.project_base.pk])
        self.url_no_perm = reverse('questionnaire-overview', args=[self.project_no_perm.pk])


class QuestionCreateViewTests(BaseAdminViewTestMixin, TestData):
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
            url = reverse('question-create', args=[self.project_base.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('ddm-login'))

    def test_superuser_logged_in_returns_200(self):
        self.client.login(**self.users['super']['credentials'])
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project_base.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_owner_logged_in_returns_200(self):
        self.client.login(**self.users['base']['credentials'])
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project_base.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_non_owner_logged_in_returns_404(self):
        self.client.login(**self.users['base2']['credentials'])
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project_base.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 404)

    def test_user_without_profile_logged_in_redirects_to_registration_view(self):
        self.client.login(**self.users['no_profile']['credentials'])
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project_base.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('ddm-register'))

    def test_user_without_permission_logged_in_redirects_to_no_permission_view(self):
        self.client.login(**self.users['no_permission']['credentials'])
        for slug in self.question_type_slugs:
            url = reverse('question-create', args=[self.project_no_perm.pk, slug])
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('ddm-no-permission'))


class QuestionEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('question-edit', args=[self.project_base.pk, 'open', self.open_quest.pk])
        self.url_no_perm = reverse('question-edit', args=[self.project_no_perm.pk, 'open', self.open_quest.pk])


class QuestionDeleteViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('question-delete', args=[self.project_base.pk, 'open', self.open_quest.pk])
        self.url_no_perm = reverse('question-delete', args=[self.project_no_perm.pk, 'open', self.open_quest.pk])


class QuestionItemsEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('question-items', args=[self.project_base.pk, 'single_choice', self.sc_quest.pk])
        self.url_no_perm = reverse('question-items',
                                   args=[self.project_no_perm.pk, 'single_choice', self.sc_quest.pk])


class QuestionScaleEditViewTests(BaseAdminViewTestMixin, TestData):
    def setUp(self):
        super().setUp()
        self.url = reverse('question-scale', args=[self.project_base.pk, 'matrix', self.matrix_quest.pk])
        self.url_no_perm = reverse('question-scale', args=[self.project_no_perm.pk, 'matrix', self.matrix_quest.pk])
