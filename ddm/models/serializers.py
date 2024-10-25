from rest_framework import serializers

from ddm.models.core import DonationProject, Participant


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DonationProject
        fields = ['pk', 'name', 'date_created']


class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')

    class Meta:
        model = Participant
        fields = ['pk', 'project', 'external_id', 'start_time', 'end_time',
                  'completed', 'extra_data']
