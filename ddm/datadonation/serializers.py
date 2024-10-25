from rest_framework import serializers

from ddm.datadonation.models import DataDonation
from ddm.encryption.serializers import SerializerDecryptionMixin


class DonationSerializer(SerializerDecryptionMixin, serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')
    data = serializers.SerializerMethodField()
    participant = serializers.IntegerField(source='participant.id')

    class Meta:
        model = DataDonation
        fields = ['time_submitted', 'consent', 'status', 'data', 'project', 'participant']
