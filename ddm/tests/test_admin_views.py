from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from ddm.models.core import (
    DonationProject, ResearchProfile, DonationBlueprint, FileUploader,
    DonationInstruction, Participant
)
from ddm.models.questions import (
    MatrixQuestion, SingleChoiceQuestion, OpenQuestion, MultiChoiceQuestion,
    SemanticDifferential, Transition
)


User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestAdminViewAuthentication(TestCase):
    """
    Tests that users with different access rights are redirected to
    the correct view.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Users
        cls.super_user_creds = {
            'username': 'superuser', 'password': '123', 'email': 'super@mail.com'
        }
        cls.super_user = User.objects.create_superuser(**cls.super_user_creds)
        ResearchProfile.objects.create(user=cls.super_user)

        cls.owner_creds = {
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        }
        cls.owner = User.objects.create_user(**cls.owner_creds)
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner)

        cls.non_owner_creds = {
            'username': 'non-owner', 'password': '123', 'email': 'non-owner@mail.com'
        }
        cls.non_owner = User.objects.create_user(**cls.non_owner_creds)
        cls.non_owner_profile = ResearchProfile.objects.create(user=cls.non_owner)

        cls.not_permitted_creds = {
            'username': 'no_per', 'password': '123', 'email': 'noperm@liam.com'
        }
        cls.not_permitted_user = User.objects.create_user(**cls.not_permitted_creds)
        cls.not_permitted_profile = ResearchProfile.objects.create(user=cls.not_permitted_user)

        cls.wo_profile_creds = {
            'username': 'no_prof', 'password': '123', 'email': 'noprof@mail.com'
        }
        cls.wo_profile_user = User.objects.create_user(**cls.wo_profile_creds)

        # Projects
        cls.project_owned = DonationProject.objects.create(
            name='Owned Project', slug='owned', owner=cls.owner_profile)
        cls.project_not_owned = DonationProject.objects.create(
            name='Not Owned Project', slug='not-owned', owner=cls.non_owner_profile)

        # Blueprint
        cls.blueprint = DonationBlueprint.objects.create(
            project=cls.project_owned,
            name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=None
        )

        # File Uploader
        cls.file_uploader = FileUploader.objects.create(
            project=cls.project_owned,
            name='basic file uploader',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE
        )

        # Instructions
        cls.instruction = DonationInstruction.objects.create(
            text='some text',
            index=1,
            file_uploader=cls.file_uploader
        )

        # Questions
        cls.open_quest = OpenQuestion.objects.create(
            project=cls.project_owned,
            blueprint=cls.blueprint,
            name='open question',
            variable_name='open_question'
        )
        cls.sc_quest = SingleChoiceQuestion.objects.create(
            project=cls.project_owned,
            blueprint=cls.blueprint,
            name='sc question',
            variable_name='sc_question'
        )
        cls.mc_quest = MultiChoiceQuestion.objects.create(
            project=cls.project_owned,
            blueprint=cls.blueprint,
            name='mc question',
            variable_name='mc_question'
        )
        cls.matrix_quest = MatrixQuestion.objects.create(
            project=cls.project_owned,
            blueprint=cls.blueprint,
            name='matrix question',
            variable_name='matrix_question'
        )
        cls.diff_quest = SemanticDifferential.objects.create(
            project=cls.project_owned,
            blueprint=cls.blueprint,
            name='diff question',
            variable_name='diff_question'
        )
        cls.trans_quest = Transition.objects.create(
            project=cls.project_owned,
            blueprint=cls.blueprint,
            name='diff question',
            variable_name='trans_question'
        )

        # Participant
        cls.participant_base = Participant.objects.create(
            project=cls.project_owned,
            start_time=timezone.now()
        )

        # Define list of admin urls for owned project.
        cls.urls = cls.get_admin_urls(cls.project_owned.pk)

        # Define list of admin urls for non-owned project.
        cls.urls_no_perm = cls.get_admin_urls(cls.project_not_owned.pk)

    @classmethod
    def get_admin_urls(cls, project_pk):
        urls = []
        project_related_views = [
            'project-edit',
            'project-delete',
            'briefing-edit',
            'debriefing-edit',
            'data-donation-overview',
            'blueprint-create',
            'questionnaire-overview'
        ]
        for view in project_related_views:
            urls.append(reverse(view, args=[project_pk]))

        blueprint_related_views = ['blueprint-edit', 'blueprint-delete']
        for view in blueprint_related_views:
            urls.append(reverse(view, args=[project_pk, cls.blueprint.pk]))

        uploader_related_views = [
            'file-uploader-edit',
            'file-uploader-delete',
            'instruction-overview',
            'instruction-create'
        ]
        for view in uploader_related_views:
            urls.append(reverse(view, args=[project_pk, cls.file_uploader.pk]))

        instruction_related_views = ['instruction-edit', 'instruction-delete']
        for view in instruction_related_views:
            urls.append(
                reverse(view, args=[project_pk, cls.file_uploader.pk, cls.instruction.pk]))

        questions = [
            ('single_choice', cls.sc_quest.pk),
            ('multi_choice', cls.mc_quest.pk),
            ('open', cls.open_quest.pk),
            ('matrix', cls.matrix_quest.pk),
            ('semantic_diff', cls.diff_quest.pk),
            ('transition', cls.trans_quest.pk)
        ]
        for question in questions:
            urls.append(
                reverse('question-create', args=[project_pk, question[0]]))

        for view in ['question-edit', 'question-delete']:
            for question in questions:
                urls.append(
                    reverse(view, args=[project_pk, question[0], question[1]]))

        item_views = [
            reverse('question-items',
                    args=[project_pk, 'single_choice', cls.sc_quest.pk]),
            reverse('question-items',
                    args=[project_pk, 'multi_choice', cls.mc_quest.pk]),
            reverse('question-items',
                    args=[project_pk, 'matrix', cls.matrix_quest.pk]),
            reverse('question-items',
                    args=[project_pk, 'semantic_diff', cls.diff_quest.pk]),
        ]
        urls += item_views

        scale_views = [
            reverse('question-scale',
                    args=[project_pk, 'matrix', cls.matrix_quest.pk]),
            reverse('question-scale',
                    args=[project_pk, 'semantic_diff', cls.diff_quest.pk]),
        ]
        urls += scale_views
        return urls

    def test_logged_out_redirects_to_login_view(self):
        for url in self.urls:
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('ddm-login'))

    def test_superuser_logged_in_returns_200(self):
        for url in self.urls:
            self.client.login(**self.super_user_creds)
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_owner_logged_in_returns_200(self):
        for url in self.urls:
            self.client.login(**self.owner_creds)
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)

    def test_non_owner_logged_in_returns_404(self):
        for url in self.urls:
            if url in [reverse('project-list'), reverse('project-create')]:
                pass
            else:
                self.client.login(**self.non_owner_creds)
                response = self.client.get(url, follow=True)
                self.assertEqual(response.status_code, 404)

    def test_user_without_profile_logged_in_redirects_to_registration_view(self):
        for url in self.urls:
            self.client.login(**self.wo_profile_creds)
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, reverse('ddm-register-researcher'))

    def test_user_wo_permission_logged_in_redirects_to_no_permission_view(self):
        for url in self.urls_no_perm:
            if url in [reverse('project-list'), reverse('project-create')]:
                pass
            else:
                self.client.login(**self.not_permitted_creds)
                response = self.client.get(url, follow=True)
                self.assertRedirects(response, reverse('ddm-no-permission'))


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestProjectListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.owner_creds = {
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'}
        cls.owner = User.objects.create_user(**cls.owner_creds)
        cls.owner_profile = ResearchProfile.objects.create(user=cls.owner)

        # Projects
        cls.project_owned = DonationProject.objects.create(
            name='Owned Project', slug='owned', owner=cls.owner_profile)

    def test_project_list_returns_correct_queryset(self):
        self.client.login(**self.owner_creds)
        response = self.client.get(reverse('project-list'))
        object_list = response.context['object_list']
        expected_queryset = DonationProject.objects.filter(owner__user=self.owner)
        self.assertQuerysetEqual(
            object_list, list(expected_queryset), ordered=False)
