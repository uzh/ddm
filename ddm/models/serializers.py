import json

from django.views.decorators.debug import sensitive_variables
from rest_framework import serializers
from rest_framework.fields import empty

from ddm.models.core import (
    DataDonation, DonationProject, QuestionnaireResponse, Participant
)
from ddm.models.questions import QuestionBase, QuestionItem


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
    meta_data = serializers.SerializerMethodField()
    responses = serializers.SerializerMethodField()
    participant = serializers.IntegerField(source='participant.id')

    class Meta:
        model = QuestionnaireResponse
        fields = ['time_submitted', 'meta_data', 'project', 'participant', 'responses']

    @sensitive_variables()
    def get_meta_data(self, obj):
        data = super().get_data(obj)
        try:
            return json.loads(data)
        except TypeError:
            return data

    @sensitive_variables()
    def get_responses(self, obj):
        """
        Creates a dictionary that only holds 'variable_name: response' pairs.
        """
        data = super().get_data(obj)
        try:
            data = json.loads(data)
        except TypeError:
            return data

        responses = dict()
        for question_id in data:
            if isinstance(data[question_id]['response'], dict):
                item_answers = data[question_id]['response']
                for item_id in item_answers:
                    try:
                        item = QuestionItem.objects.all().get(id=item_id)
                    except QuestionItem.DoesNotExist:
                        # Item has been deleted.
                        continue
                    var_name = item.question.variable_name
                    value = item.value
                    responses[f'{var_name}-{value}'] = item_answers[item_id]
                pass
            else:
                try:
                    question = QuestionBase.objects.all().get(id=question_id)
                except QuestionBase.DoesNotExist:
                    # Question has been deleted.
                    continue
                var_name = question.variable_name
                responses[var_name] = data[question_id]['response']
        return responses


class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.IntegerField(source='project.id')

    class Meta:
        model = Participant
        fields = ['pk', 'project', 'external_id', 'start_time', 'end_time',
                  'completed', 'extra_data']
