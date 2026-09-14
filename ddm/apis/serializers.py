import contextlib
import json

from django.views.decorators.debug import sensitive_variables
from rest_framework import serializers

from ddm.datadonation.models import DataDonation
from ddm.encryption.serializers import SerializerDecryptionMixin
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.questionnaire.models import QuestionnaireResponse


class ProjectSerializer(serializers.ModelSerializer):
    date_created = serializers.DateTimeField(format="iso-8601")

    class Meta:
        model = DonationProject
        fields = [
            "url_id",
            "slug",
            "name",
            "date_created",
            "active",
            "contact_information",
            "data_protection_statement",
            "url_parameter_enabled",
            "expected_url_parameters",
        ]


class DataDonationSerializer(SerializerDecryptionMixin, serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    participant = serializers.CharField(source="participant.external_id")
    time_submitted = serializers.DateTimeField(format="iso-8601")

    class Meta:
        model = DataDonation
        fields = [
            "participant",
            "data",
            "time_submitted",
            "data_extraction_state",
            "consent",
            "n_data_entries",
        ]


def is_flat_dict(d: dict) -> bool:
    """Checks that none of the dictionary values are a dict or a list."""
    return all(not isinstance(v, (dict, list)) for v in d.values())


class ResponseSerializer(SerializerDecryptionMixin, serializers.ModelSerializer):
    participant = serializers.CharField(source="participant.external_id")
    response_data = serializers.SerializerMethodField()
    time_submitted = serializers.DateTimeField(format="iso-8601")
    questionnaire_complete = serializers.BooleanField(source="is_complete")

    class Meta:
        model = QuestionnaireResponse
        fields = [
            "participant",
            "response_data",
            "time_submitted",
            "questionnaire_complete",
        ]

    @sensitive_variables()
    def get_response_data(self, obj: QuestionnaireResponse) -> dict:
        """
        Creates a dictionary that only holds 'variable_name: response' pairs.

        Note: Question/item variable names are resolved from
        `self.context["question_variable_names"]`/`["item_variable_names"]`
        (built once per request by the view) rather than queried per field,
        to avoid an O(responses x fields) query blowup.
        """
        data = super().get_data(obj)
        with contextlib.suppress(TypeError):
            data = json.loads(data)

        # For backward compatibility: Check if responses have been saved in old
        # or new structure; if so, use legacy function.
        if not is_flat_dict(data):
            return self.legacy_get_response_data(data)

        question_names = self.context.get("question_variable_names", {})
        item_names = self.context.get("item_variable_names", {})

        responses = {}
        for response_id in data:
            if response_id.startswith("question-"):
                question_id = response_id.removeprefix("question-")
                var_name = question_names.get(int(question_id))
                if var_name is None:
                    # Question has been deleted.
                    continue
                responses[var_name] = data[response_id]

            if response_id.startswith("item-"):
                item_id = response_id.removeprefix("item-")
                var_name = item_names.get(int(item_id))
                if var_name is None:
                    # Item has been deleted.
                    continue
                responses[var_name] = data[response_id]

        return responses

    def legacy_get_response_data(self, data: dict) -> dict:
        """
        Used to support extracting response data that has been saved in the old
        response structure (DDM <= v2.0.2).
        """
        question_names = self.context.get("question_variable_names", {})
        item_names = self.context.get("item_variable_names", {})

        responses = {}
        for question_id in data:
            var_name = question_names.get(int(question_id))
            if var_name is None:
                # Question has been deleted.
                continue

            if isinstance(data[question_id]["response"], dict):
                item_answers = data[question_id]["response"]
                for item_id in item_answers:
                    item_var_name = item_names.get(int(item_id))
                    if item_var_name is None:
                        # Item has been deleted.
                        continue
                    responses[item_var_name] = item_answers[item_id]
            else:
                responses[var_name] = data[question_id]["response"]
        return responses


class ResponseSerializerWithSnapshot(ResponseSerializer):
    questionnaire_snapshot = serializers.SerializerMethodField()

    class Meta:
        model = QuestionnaireResponse
        fields = [
            "participant",
            "time_submitted",
            "questionnaire_snapshot",
            "response_data",
            "questionnaire_config",
            "questionnaire_complete",
        ]

    @sensitive_variables()
    def get_questionnaire_snapshot(self, obj: QuestionnaireResponse) -> dict:
        data = super().get_data(obj)
        try:
            return json.loads(data)
        except TypeError:
            return data


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = [
            "external_id",
            "start_time",
            "end_time",
            "completed",
            "url_parameter",
            "extra_data",
            "current_step",
        ]
