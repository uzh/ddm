from rest_framework import serializers

from ddm.encryption.serializers import SerializerDecryptionMixin
from ddm.models.core import DataDonation, DonationProject, Participant


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DonationProject
        fields = ['pk', 'name', 'date_created']


class DonationSerializer(SerializerDecryptionMixin, serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')
    data = serializers.SerializerMethodField()
    participant = serializers.IntegerField(source='participant.id')

    class Meta:
        model = DataDonation
        fields = ['time_submitted', 'consent', 'status', 'data', 'project', 'participant']


class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')

    class Meta:
        model = Participant
        fields = ['pk', 'project', 'external_id', 'start_time', 'end_time',
                  'completed', 'extra_data']
