from ddm.models.core import Participant
from rest_framework import serializers


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['external_id', 'extra_data', 'completed']
