from rest_framework import serializers

from ddm.participation.models import Participant


class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')

    class Meta:
        model = Participant
        fields = ['pk', 'project', 'external_id', 'start_time', 'end_time',
                  'completed', 'extra_data']
