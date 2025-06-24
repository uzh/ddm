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


def is_flat_dict(d: dict) -> bool:
    """Checks that none of the dictionary values are a dict or a list."""
    return all(not isinstance(v, (dict, list)) for v in d.values())


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
            data = data

        # For backward compatibility: Check if responses have been saved in old
        # or new structure; if so, use legacy function.
        if not is_flat_dict(data):
            return self.legacy_get_response_data(data)

        responses = dict()
        for response_id in data.keys():
            if response_id.startswith('question-'):
                question_id = response_id.lstrip('question-')
                try:
                    question = QuestionBase.objects.all().get(id=question_id)
                except QuestionBase.DoesNotExist:
                    # Question has been deleted.
                    continue
                var_name = question.variable_name
                responses[var_name] = data[response_id]

            if response_id.startswith('item-'):
                item_id = response_id.lstrip('item-')
                try:
                    item = QuestionItem.objects.all().get(id=item_id)
                except QuestionItem.DoesNotExist:
                    # Item has been deleted.
                    continue
                var_name = item.variable_name
                responses[var_name] = data[response_id]

        return responses

    def legacy_get_response_data(self, data):
        """
        Used to support extracting response data that has been saved in the old
        response structure (DDM <= v2.0.2).
        """
        responses = dict()
        for question_id in data.keys():
            try:
                question = QuestionBase.objects.all().get(id=question_id)
                var_name = question.variable_name
            except QuestionBase.DoesNotExist:
                # Question has been deleted.
                continue

            if isinstance(data[question_id]['response'], dict):
                item_answers = data[question_id]['response']
                for item_id in item_answers.keys():
                    try:
                        item = QuestionItem.objects.all().get(id=int(item_id))
                    except QuestionItem.DoesNotExist:
                        # Item has been deleted.
                        continue
                    var_name = item.variable_name
                    responses[var_name] = item_answers[item_id]
                pass
            else:
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
            'response_data',
            'questionnaire_config'
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
            'extra_data',
            'current_step'
        ]
