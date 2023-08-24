from django.urls import path
from rest_framework import routers

from ddm_pooled.views import ParticipantViewSet, PoolDonateView


router = routers.SimpleRouter()
router.register(r'participants', ParticipantViewSet, 'participant')

urlpatterns = [
    path(r'<slug:slug>/pool_donate', PoolDonateView.as_view(), name='ddm-pool-donate')
]
urlpatterns += router.urls
