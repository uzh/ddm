from ddm_pooled.models import PoolParticipant
from rest_framework import serializers


class ParticipantSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status')

    class Meta:
        model = PoolParticipant
        fields = ['external_id', 'pool_id', 'status']
