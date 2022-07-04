from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from ddm.models import (
    ResearchProfile, DonationProject, DonationBlueprint, ZippedBlueprint,
    DonationInstruction, MatrixQuestion, SingleChoiceQuestion, OpenQuestion, Participant
)


User = get_user_model()


@override_settings(DDM_SETTINGS={'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)mail\.com$', })
class TestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Users
        cls.users = {}

        super_user_credentials = {'username': 'super_user', 'password': '123', 'email': 'super@mail.com'}
        super_user = User.objects.create_superuser(**super_user_credentials)
        super_user_profile = ResearchProfile.objects.create(user=super_user)
        cls.users['super'] = {
            'credentials': super_user_credentials,
            'user': super_user,
            'profile': super_user_profile}

        base_user_credentials = {'username': 'base_user', 'password': '123', 'email': 'base@mail.com'}
        base_user = User.objects.create_user(**base_user_credentials)
        base_user_profile = ResearchProfile.objects.create(user=base_user)
        cls.users['base'] = {
            'credentials': base_user_credentials,
            'user': base_user,
            'profile': base_user_profile}

        base_user2_credentials = {'username': 'base_user2', 'password': '123', 'email': 'base2@mail.com'}
        base_user2 = User.objects.create_user(**base_user2_credentials)
        base_user2_profile = ResearchProfile.objects.create(user=base_user2)
        cls.users['base2'] = {
            'credentials': base_user2_credentials,
            'user': base_user2,
            'profile': base_user2_profile}

        base_user3_credentials = {'username': 'base_user3', 'password': '123', 'email': 'base3@mail.com'}
        base_user3 = User.objects.create_user(**base_user3_credentials)
        base_user3_profile = ResearchProfile.objects.create(user=base_user3)
        cls.users['base3'] = {
            'credentials': base_user3_credentials,
            'user': base_user3,
            'profile': base_user3_profile}

        user_wo_profile_credentials = {'username': 'no_prof', 'password': '123', 'email': 'noprof@mail.com'}
        user_wo_profile = User.objects.create_user(**user_wo_profile_credentials)
        cls.users['no_profile'] = {
            'credentials': user_wo_profile_credentials,
            'user': user_wo_profile,
            'profile': None}

        user_wo_permission_credentials = {'username': 'no_per', 'password': '123', 'email': 'noperm@liam.com'}
        user_wo_permission = User.objects.create_user(**user_wo_permission_credentials)
        user_wo_permission_profile = ResearchProfile.objects.create(user=user_wo_permission)
        cls.users['no_permission'] = {
            'credentials': user_wo_permission_credentials,
            'user': user_wo_permission,
            'profile': user_wo_permission_profile}

        # Projects
        cls.project_base = DonationProject.objects.create(
            name='Base Project', slug='base', owner=cls.users['base']['profile'])
        cls.project_base2 = DonationProject.objects.create(
            name='Base2 Project', slug='base-2', owner=cls.users['base2']['profile'])
        cls.project_no_perm = DonationProject.objects.create(
            name='No Perm Project', slug='no-perm', owner=cls.users['no_permission']['profile'])

        # Blueprints
        cls.don_bp = DonationBlueprint.objects.create(
            project=cls.project_base,
            name='donation blueprint',
            expected_fields='"a", "b"',
            extracted_fields='"a"'
        )
        cls.zip_bp = ZippedBlueprint.objects.create(
            name='zipped blueprint',
            project=cls.project_base
        )

        # Questions
        cls.open_quest = OpenQuestion.objects.create(
            project=cls.project_base,
            blueprint=cls.don_bp,
            name='open question',
            variable_name='open_question'
        )
        cls.sc_quest = SingleChoiceQuestion.objects.create(
            project=cls.project_base,
            blueprint=cls.don_bp,
            name='sc question',
            variable_name='sc_question'
        )
        cls.matrix_quest = MatrixQuestion.objects.create(
            project=cls.project_base,
            blueprint=cls.don_bp,
            name='matrix question',
            variable_name='matrix_question'
        )
        cls.instruction = DonationInstruction.objects.create(
            text='some text',
            index=1,
            blueprint=cls.don_bp
        )

        # Participant
        cls.participant_base = Participant.objects.create(
            project=cls.project_base,
            start_time=timezone.now()
        )
