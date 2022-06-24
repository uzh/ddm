from rest_framework import serializers

from ddm.models.data_donations import DataDonation
from ddm.models.projects import DonationProject, QuestionnaireResponse


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DonationProject
        fields = ['name', 'date_created']


class DonationSerializer(serializers.HyperlinkedModelSerializer):
    project = ProjectSerializer(many=False, read_only=True)

    class Meta:
        model = DataDonation
        fields = ['time_submitted', 'consent', 'status', 'data', 'project']


class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    project = ProjectSerializer(many=False, read_only=True)

    class Meta:
        model = QuestionnaireResponse
        fields = ['time_submitted', 'data', 'project']
