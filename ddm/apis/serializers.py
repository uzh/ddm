import json

from django.views.decorators.debug import sensitive_variables
from rest_framework import serializers

from ddm.datadonation.models import DataDonation
from ddm.encryption.serializers import SerializerDecryptionMixin
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.questionnaire.models import QuestionnaireResponse, QuestionBase, QuestionItem


class ProjectSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format='iso-8601')

    class Meta:
        model = DonationProject
        fields = [
            'url_id',
            'slug',
            'name',
            'date_created',
            'active',
            'contact_information',
            'data_protection_statement',
            'url_parameter_enabled',
            'expected_url_parameters'
        ]


class DataDonationSerializer(SerializerDecryptionMixin, serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    participant = serializers.CharField(source='participant.external_id')
    time_submitted = serializers.DateTimeField(format='iso-8601')

    class Meta:
        model = DataDonation
        fields = [
            'participant',
            'data',
            'time_submitted',
            'status',
            'consent',
        ]


class ResponseSerializer(SerializerDecryptionMixin, serializers.ModelSerializer):
    participant = serializers.CharField(source='participant.external_id')
    response_data = serializers.SerializerMethodField()
    time_submitted = serializers.DateTimeField(format='iso-8601')

    class Meta:
        model = QuestionnaireResponse
        fields = [
            'participant',
            'response_data',
            'time_submitted'
        ]

    @sensitive_variables()
    def get_response_data(self, obj):
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


class ResponseSerializerWithSnapshot(ResponseSerializer):
    questionnaire_snapshot = serializers.SerializerMethodField()

    class Meta:
        model = QuestionnaireResponse
        fields = [
            'participant',
            'time_submitted',
            'questionnaire_snapshot',
            'response_data'
        ]

    @sensitive_variables()
    def get_questionnaire_snapshot(self, obj):
        data = super().get_data(obj)
        try:
            return json.loads(data)
        except TypeError:
            return data


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = [
            'external_id',
            'start_time',
            'end_time',
            'completed',
            'extra_data'
        ]
