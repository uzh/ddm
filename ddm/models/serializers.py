import json

from django.views.decorators.debug import sensitive_variables
from rest_framework import serializers
from rest_framework.fields import empty

from ddm.models.core import (
    DataDonation, DonationProject, QuestionnaireResponse, Participant
)


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DonationProject
        fields = ['pk', 'name', 'date_created']


class SerializerDecryptionMixin:
    """
    Allows to pass the secret for the decryption of super secret projects to
    the serializer on init.
    """
    @sensitive_variables()
    def __init__(self, instance=None, data=empty, decryptor=None, **kwargs):
        self.decryptor = decryptor
        self.secret = kwargs.pop('secret', None)
        super().__init__(instance=instance, data=data, **kwargs)

    @sensitive_variables()
    def get_data(self, obj):
        if not self.secret:
            self.secret = obj.project.secret_key
        return obj.get_decrypted_data(self.secret, obj.project.get_salt(), self.decryptor)


class DonationSerializer(SerializerDecryptionMixin, serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')
    data = serializers.SerializerMethodField()
    participant = serializers.IntegerField(source='participant.id')

    class Meta:
        model = DataDonation
        fields = ['time_submitted', 'consent', 'status', 'data', 'project', 'participant']


class ResponseSerializer(SerializerDecryptionMixin, serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')
    data = serializers.SerializerMethodField()
    participant = serializers.IntegerField(source='participant.id')

    class Meta:
        model = QuestionnaireResponse
        fields = ['time_submitted', 'data', 'project', 'participant']

    @sensitive_variables()
    def get_data(self, obj):
        data = super().get_data(obj)
        try:
            return json.loads(data)
        except TypeError:
            return data


class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')

    class Meta:
        model = Participant
        fields = ['pk', 'project', 'external_id', 'start_time', 'end_time',
                  'completed', 'extra_data']
