from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from ddm.models.core import Participant, ResearchProfile, DonationProject
from ddm.tests.test_participation_flow import ParticipationFlowBaseTestCase
from ddm_pooled.models import PooledProject
from ddm_pooled.settings import POOL_KW, PROJECT_KW


User = get_user_model()


class ParticipantAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(**{
            'username': 'u', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=cls.user)
        project = DonationProject.objects.create(
            name='Base Project', slug='base', owner=profile)
        cls.pooled_project = PooledProject.objects.create(
            project=project, external_id='external_id')
        Participant.objects.create(
            project=project,
            external_id='abc',
            start_time=timezone.now(),
            extra_data={'pool_id': 'test_pool'}
        )

    def test_get_participants(self):
        """
        Ensure the correct participant information is retrieved.
        """
        url = reverse('participant-list')
        data = {
            'extra_data': {'pool_id': 'test_pool'},
            'external_id': '1',
            'completed': False
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            url, {POOL_KW: 'test_pool', PROJECT_KW: 'external_id'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertCountEqual(dict(response.data[0]), data)

    def test_get_participants_without_poolid(self):
        """
        Ensure query without pool_id raises 400.
        """
        url = reverse('participant-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestPoolDonateView(ParticipationFlowBaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.pooled_project = PooledProject.objects.create(
            project=cls.project_base, external_id='abc')

    def setUp(self):
        super().setUp()
        self.initialize_project_and_session()
        self.participant = self.get_participant(self.project_base.pk)
        self.participant.current_step = 3
        self.participant.save()

    def test_redirect_to_donation_question(self):
        response = self.client.get(self.debriefing_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse('ddm-pool-donate', args=[self.project_base.slug]))

    def test_post_valid_form(self):
        response = self.client.post(
            reverse('ddm-pool-donate', args=[self.project_base.slug]),
            {'donation_consent': '1'}
        )
        self.assertRedirects(response, reverse('debriefing', args=[self.project_base.slug]))
        self.assertEqual(response.status_code, 302)
        self.participant.refresh_from_db()
        self.assertEqual(self.participant.extra_data['pool_donate'], True)

    def test_post_invalid_form(self):
        response = self.client.post(
            reverse('ddm-pool-donate', args=[self.project_base.slug]),
            {'donation_consent': 'fubar'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm_pooled/pool_donation_consent.html')

    def test_skip_donation_question(self):
        self.pooled_project.get_donation_consent = False
        self.pooled_project.save()
        response = self.client.get(self.debriefing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ddm/public/debriefing.html')
