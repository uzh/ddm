from django.contrib import auth
from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.views.generic import TemplateView

from ddm.auth.views import DDMAuthMixin
from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestNoPermissionView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_creds = {
            "username": "owner",
            "password": "123",
            "email": "owner@mail.com",
        }
        valid_user = User.objects.create_user(**cls.valid_creds)
        ResearchProfile.objects.create(user=valid_user)

        cls.not_permitted_creds = {
            "username": "no_per",
            "password": "123",
            "email": "noperm@liam.com",
        }
        not_permitted_user = User.objects.create_user(**cls.not_permitted_creds)
        ResearchProfile.objects.create(user=not_permitted_user)

    def test_ddm_no_permission_view_200_if_not_permitted(self):
        self.client.login(**self.not_permitted_creds)
        response = self.client.get(reverse("ddm_auth:no_permission"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_ddm_no_permission_view_200_if_anonymous(self):
        response = self.client.get(reverse("ddm_auth:no_permission"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_ddm_no_permission_view_redirect_to_project_list_if_permitted(self):
        self.client.login(**self.valid_creds)
        response = self.client.get(reverse("ddm_auth:no_permission"), follow=True)
        self.assertRedirects(response, reverse("ddm_projects:list"))


class TestProjectTokenView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_creds = {
            "username": "owner",
            "password": "123",
            "email": "owner@mail.com",
        }
        cls.valid_user = User.objects.create_user(**cls.valid_creds)
        valid_profile = ResearchProfile.objects.create(user=cls.valid_user)
        cls.project = DonationProject.objects.create(
            name="test-project", slug="test", owner=valid_profile
        )

        cls.not_permitted_creds = {
            "username": "no_per",
            "password": "123",
            "email": "noperm@liam.com",
        }
        not_permitted_user = User.objects.create_user(**cls.not_permitted_creds)
        ResearchProfile.objects.create(user=not_permitted_user)

    def test_200_if_permitted(self):
        self.client.login(**self.valid_creds)
        response = self.client.get(
            reverse("ddm_auth:project_token", args=[self.project.url_id]), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_permitted(self):
        self.client.login(**self.not_permitted_creds)
        response = self.client.get(
            reverse("ddm_auth:project_token", args=[self.project.url_id]), follow=True
        )
        self.assertRedirects(response, reverse("ddm_auth:no_permission"))

    def test_redirect_if_anonymous(self):
        self.client.logout()
        response = self.client.get(
            reverse("ddm_auth:project_token", args=[self.project.url_id]), follow=True
        )
        self.assertRedirects(response, reverse("ddm_login"))


class TestView(DDMAuthMixin, TemplateView):
    template_name = "ddm_auth/no_permission.html"


@override_settings(DDM_SETTINGS={"EMAIL_PERMISSION_CHECK": r".*(\.|@)mail\.com$"})
class TestDDMAuthMixin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_creds = {
            "username": "owner",
            "password": "123",
            "email": "owner@mail.com",
        }
        cls.valid_user = User.objects.create_user(**cls.valid_creds)
        valid_profile = ResearchProfile.objects.create(user=cls.valid_user)
        cls.project = DonationProject.objects.create(
            name="test-project", slug="test", owner=valid_profile
        )

        cls.not_permitted_creds = {
            "username": "no_per",
            "password": "123",
            "email": "noperm@liam.com",
        }
        cls.not_permitted_user = User.objects.create_user(**cls.not_permitted_creds)
        ResearchProfile.objects.create(user=cls.not_permitted_user)

        cls.wo_profile_creds = {
            "username": "no_prof",
            "password": "123",
            "email": "noprof@mail.com",
        }
        cls.user_wo_profile = User.objects.create_user(**cls.wo_profile_creds)

        cls.not_owner_creds = {
            "username": "notowner",
            "password": "123",
            "email": "notowner@mail.com",
        }
        cls.not_owner = User.objects.create_user(**cls.not_owner_creds)
        ResearchProfile.objects.create(user=cls.not_owner)

        cls.view = TestView.as_view()
        cls.factory = RequestFactory()

    def test_dispatch_anonymous_user(self):
        anonymous_user = auth.get_user(self.client)
        request = self.factory.get("/test-url/")
        request.user = anonymous_user
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("ddm_login")))

    def test_dispatch_non_permitted_user(self):
        request = self.factory.get("/test-url/")
        request.user = self.not_permitted_user
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("ddm_auth:no_permission")))

    def test_dispatch_user_without_profile(self):
        request = self.factory.get("/test-url/")
        request.user = self.user_wo_profile
        self.assertFalse(
            ResearchProfile.objects.filter(user=self.user_wo_profile).exists()
        )
        with self.assertRaises(Http404):
            _ = self.view(request)
        self.assertTrue(
            ResearchProfile.objects.filter(user=self.user_wo_profile).exists()
        )

    def test_dispatch_not_owner_user(self):
        request = self.factory.get("/test-url/")
        request.user = self.not_owner
        with self.assertRaises(Http404):
            self.view(request, project_url_id=self.project.url_id)

    def test_dispatch_valid_user(self):
        request = self.factory.get("/test-url/")
        request.user = self.valid_user
        response = self.view(request, project_url_id=self.project.url_id)
        self.assertEqual(response.status_code, 200)

    def test_dispatch_anonymous_user_post(self):
        """POST should be redirected to login the same way GET is."""
        anonymous_user = auth.get_user(self.client)
        request = self.factory.post("/test-url/")
        request.user = anonymous_user
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("ddm_login")))

    def test_dispatch_non_permitted_user_post(self):
        """POST should be redirected to the no-permission page the same way GET is."""
        request = self.factory.post("/test-url/")
        request.user = self.not_permitted_user
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("ddm_auth:no_permission")))

    def test_dispatch_anonymous_user_delete(self):
        """A non-GET/POST method must not bypass the authentication check."""
        anonymous_user = auth.get_user(self.client)
        request = self.factory.delete("/test-url/")
        request.user = anonymous_user
        with self.assertRaises(Http404):
            self.view(request)

    def test_dispatch_non_permitted_user_delete(self):
        """A non-GET/POST method must not bypass the permission check."""
        request = self.factory.delete("/test-url/")
        request.user = self.not_permitted_user
        with self.assertRaises(Http404):
            self.view(request)

    def test_dispatch_not_owner_user_delete(self):
        """A non-GET/POST method must not bypass the project-ownership check."""
        request = self.factory.delete("/test-url/")
        request.user = self.not_owner
        with self.assertRaises(Http404):
            self.view(request, project_url_id=self.project.url_id)

    def test_dispatch_valid_user_delete(self):
        """A DELETE from the project's owner passes the mixin's checks and
        reaches the underlying view, which returns 405 since TestView (a
        plain TemplateView) implements no delete() handler of its own."""
        request = self.factory.delete("/test-url/")
        request.user = self.valid_user
        response = self.view(request, project_url_id=self.project.url_id)
        self.assertEqual(response.status_code, 405)
