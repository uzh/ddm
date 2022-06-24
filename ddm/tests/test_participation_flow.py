from django.test import Client
from django.urls import reverse
from django.utils import timezone

from ddm.models import DataDonation, Participant
from ddm.tests.base import TestData


class ParticipationFlowBaseTestCase(TestData):

    def setUp(self):
        # URLs for project with questionnaire.
        self.entry_url = reverse('project-entry', args=[self.project_base.slug])
        self.dd_url = reverse('data-donation', args=[self.project_base.slug])
        self.quest_url = reverse('questionnaire', args=[self.project_base.slug])
        self.exit_url = reverse('project-exit', args=[self.project_base.slug])

        # URLs for project without questionnaire.
        self.entry_url_no = reverse('project-entry', args=[self.project_base2.slug])
        self.dd_url_no = reverse('data-donation', args=[self.project_base2.slug])
        self.quest_url_no = reverse('questionnaire', args=[self.project_base2.slug])
        self.exit_url_no = reverse('project-exit', args=[self.project_base2.slug])

        # URLs for non-existing project.
        self.entry_url_invalid = reverse('project-entry', args=['nope'])
        self.dd_url_invalid = reverse('data-donation', args=['nope'])
        self.quest_url_invalid = reverse('questionnaire', args=['nope'])
        self.exit_url_invalid = reverse('project-exit', args=['nope'])

    def initialize_project_and_session(self):
        self.client = Client()
        self.client.get(self.entry_url)
        self.client.get(self.entry_url_no)

    def create_data_donation(self):
        # Create a data donation for project 1.
        participant_id = self.client.session['projects'][f'{self.project_base.pk}']['participant_id']
        participant = Participant.objects.get(pk=int(participant_id))
        DataDonation.objects.create(
            project=self.project_base,
            blueprint=self.don_bp,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            status='{}',
            data='{}'
        )


class TestEntryView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()

    def test_project_entry_view_registers_project(self):
        self.client.get(self.entry_url)
        session = self.client.session
        expected_keys = ['steps', 'data', 'completed', 'participant_id']
        assert set(expected_keys).issubset(set(session['projects'][f'{self.project_base.pk}'].keys()))

    def test_project_entry_view_registers_participant(self):
        nr_participants_before = len(Participant.objects.all())
        self.client.get(self.entry_url)
        self.assertGreater(len(Participant.objects.all()), nr_participants_before)
        self.assertIsNotNone(self.client.session['projects'][f'{self.project_base.pk}']['participant_id'])

    def test_project_entry_view_GET_valid_url(self):
        response = self.client.get(self.entry_url)
        project_session = self.client.session['projects'][f'{self.project_base.pk}']
        self.assertEqual(project_session['steps']['project-entry']['state'], 'started')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/entry_page.html')

    def test_project_entry_view_GET_invalid_url(self):
        response = self.client.get(self.entry_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_project_entry_POST(self):
        response = self.client.post(self.entry_url)
        project_session = self.client.session['projects'][f'{self.project_base.pk}']
        self.assertEqual(project_session['steps']['project-entry']['state'], 'completed')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dd_url)


class TestDonationView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        self.create_data_donation()
        session = self.client.session
        session['projects'][f'{self.project_base.pk}']['steps']['project-entry']['state'] = 'completed'
        session.save()

    def test_data_donation_GET_valid_url(self):
        response = self.client.get(self.dd_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/data_donation.html')

    def test_data_donation_GET_invalid_url(self):
        response = self.client.get(self.dd_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_data_donation_POST_redirect(self):
        response = self.client.post(self.dd_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.quest_url)


class TestQuestionnaireView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        self.create_data_donation()
        session = self.client.session
        session['projects'][f'{self.project_base.pk}']['steps']['project-entry']['state'] = 'completed'
        session['projects'][f'{self.project_base.pk}']['steps']['data-donation']['state'] = 'completed'
        session['projects'][f'{self.project_base2.pk}']['steps']['project-entry']['state'] = 'completed'
        session['projects'][f'{self.project_base2.pk}']['steps']['data-donation']['state'] = 'completed'
        session.save()

    def test_questionnaire_GET_valid_url(self):
        response = self.client.get(self.quest_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/questionnaire.html')

    def test_questionnaire_GET_invalid_url(self):
        response = self.client.get(self.quest_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_questionnaire_GET_no_questionnaire(self):
        good_response = self.client.get(self.quest_url_no)
        self.assertRedirects(good_response, self.exit_url_no)

    def test_questionnaire_POST_redirect(self):
        response = self.client.post(self.quest_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.exit_url)


class TestExitView(ParticipationFlowBaseTestCase):

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        session = self.client.session
        session['projects'][f'{self.project_base.pk}']['steps']['project-entry']['state'] = 'completed'
        session['projects'][f'{self.project_base.pk}']['steps']['data-donation']['state'] = 'completed'
        session['projects'][f'{self.project_base.pk}']['steps']['questionnaire']['state'] = 'completed'
        session.save()

    def test_project_exit_GET_valid_url(self):
        response = self.client.get(self.exit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/end.html')

    def test_project_exit_GET_invalid_url(self):
        response = self.client.get(self.exit_url_invalid, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_project_exit_POST(self):
        response = self.client.post(self.exit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/end.html')


# TODO: Add Class TestViewsRerouting(TestCase)
