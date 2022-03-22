from django.test import SimpleTestCase
from django.urls import reverse, resolve
from ddm.views import (
    ProjectEntry, DataUpload, QuestionnaireDisplay, ProjectExit
)


class TestPublicProjectUrls(SimpleTestCase):

    def test_project_entry_url_resolves(self):
        url = reverse('project-entry', args=['project-slug'])
        self.assertEqual(resolve(url).func.view_class, ProjectEntry)

    def test_project_datadonation_url_resolves(self):
        url = reverse('data-donation', args=['project-slug'])
        self.assertEqual(resolve(url).func.view_class, DataUpload)

    def test_project_questionnaire_url_resolves(self):
        url = reverse('questionnaire', args=['project-slug'])
        self.assertEqual(resolve(url).func.view_class, QuestionnaireDisplay)

    def test_project_exit_url_resolves(self):
        url = reverse('project-exit', args=['project-slug'])
        self.assertEqual(resolve(url).func.view_class, ProjectExit)
