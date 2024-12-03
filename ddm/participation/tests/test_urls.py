from django.test import SimpleTestCase
from django.urls import reverse, resolve
import ddm.participation.views as participation_views


class TestParticipationFlowUrls(SimpleTestCase):

    def test_project_briefing_url_resolves(self):
        url = reverse('ddm_participation:briefing', args=['project-slug'])
        self.assertEqual(
            resolve(url).func.view_class,
            participation_views.BriefingView
        )

    def test_project_datadonation_url_resolves(self):
        url = reverse('ddm_participation:datadonation', args=['project-slug'])
        self.assertEqual(
            resolve(url).func.view_class,
            participation_views.DataDonationView
        )

    def test_project_questionnaire_url_resolves(self):
        url = reverse('ddm_participation:questionnaire', args=['project-slug'])
        self.assertEqual(
            resolve(url).func.view_class,
            participation_views.QuestionnaireView
        )

    def test_project_debriefing_url_resolves(self):
        url = reverse('ddm_participation:debriefing', args=['project-slug'])
        self.assertEqual(
            resolve(url).func.view_class,
            participation_views.DebriefingView
        )
