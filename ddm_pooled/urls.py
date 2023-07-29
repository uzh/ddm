from django.urls import path
from rest_framework import routers

from ddm_pooled.views import ParticipantViewSet, DonationViewSet, PoolDonateView


router = routers.SimpleRouter()
router.register(r'participants', ParticipantViewSet, 'participant')

urlpatterns = [
    path(r'<slug:slug>/pool_donate', PoolDonateView.as_view(), name='ddm-pool-donate'),
    path(r'donations', DonationViewSet.as_view({'get': 'retrieve'}), name='donation-detail')
]
urlpatterns += router.urls
