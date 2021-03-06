from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.forms import ProjectCreateForm
from ddm.models import ResearchProfile


User = get_user_model()


class TestProjectCreateForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_credentials = {'username': 'user', 'password': '123', 'email': 'base@mail.com'}
        user = User.objects.create_user(**user_credentials)
        cls.user_profile = ResearchProfile.objects.create(user=user)

    def test_form_creates_normal_project(self):
        post_data = {'name': 'normal project', 'slug': 'normal-project',
                     'super_secret': False, 'secret': 'supersecretsecret',
                     'owner': self.user_profile}
        form = ProjectCreateForm(post_data)
        project = form.save()
        self.assertEqual(b'', project.public_key)

    def test_form_creates_super_secret_project(self):
        post_data = {'name': 'secret-project', 'slug': 'secret-project',
                     'super_secret': True, 'secret': 'supersecretsecret',
                     'owner': self.user_profile}
        form = ProjectCreateForm(post_data)
        project = form.save()
        self.assertNotEqual(b'', project.public_key)

    def test_form_raises_error_if_super_secret_without_secret(self):
        post_data = {'name': 'project', 'slug': 'project',
                     'super_secret': True, 'secret': '',
                     'owner': self.user_profile}
        form = ProjectCreateForm(post_data)
        self.assertFalse(form.is_valid())
