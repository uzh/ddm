from rest_framework import serializers

from ddm.models.data_donations import DataDonation
from ddm.models.projects import DonationProject, QuestionnaireResponse


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DonationProject
        fields = ['pk', 'name', 'date_created']


class DonationSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')
    data = serializers.CharField(source='get_decrypted_data')
    participant = serializers.IntegerField(source='participant.id')

    class Meta:
        model = DataDonation
        fields = ['time_submitted', 'consent', 'status', 'data', 'project', 'participant']


class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')
    data = serializers.CharField(source='get_decrypted_data')
    participant = serializers.IntegerField(source='participant.id')

    class Meta:
        model = QuestionnaireResponse
        fields = ['time_submitted', 'data', 'project', 'participant']
