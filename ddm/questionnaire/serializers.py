import json

from rest_framework import serializers
from django.views.decorators.debug import sensitive_variables

from ddm.encryption.serializers import SerializerDecryptionMixin
from ddm.questionnaire.models import QuestionBase, QuestionItem, QuestionnaireResponse


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
