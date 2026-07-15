import json
import random

from rest_framework import serializers

from ddm.core.utils.user_content.template import render_user_content
from ddm.datadonation.models import (
    BlueprintFilePath,
    DonationBlueprint,
    DonationInstruction,
    FileUploader,
    ProcessingRule,
)
from ddm.participation.utils import (
    get_filter_source_config_id,
    get_filter_target_config_id,
)
from ddm.questionnaire.constants import QuestionType
from ddm.questionnaire.models import (
    FilterCondition,
    QuestionBase,
    QuestionItem,
    ScalePoint,
)


class ProcessingRuleSerializer(serializers.ModelSerializer):
    """Serializes a ProcessingRule instance into the format expected by the frontend.

    see also: frontend/DDMUploader/src/types/ExtractionRule.ts
    """

    class Meta:
        model = ProcessingRule
        fields = [
            "id",
            "field",
            "regex_field",
            "comparison_operator",
            "comparison_value",
            "replacement_value",
        ]


class BlueprintFilePathSerializer(serializers.ModelSerializer):
    """Serializes a BlueprintFilePath instance into the format expected by the frontend.

    see also: frontend/DDMUploader/src/types/ExtractionRule.ts
    """

    class Meta:
        model = BlueprintFilePath
        fields = ["path", "is_regex"]


class BlueprintSerializer(serializers.ModelSerializer):
    """Serializes a DonationBlueprint instance into the format expected by the frontend.

    see also: frontend/DDMUploader/src/types/Blueprint.ts
    """

    name = serializers.CharField(source="display_name")
    format = serializers.CharField(source="exp_file_format")
    expected_fields = serializers.SerializerMethodField()
    exp_fields_regex_matching = serializers.BooleanField(
        source="expected_fields_regex_matching"
    )
    fields_to_extract = serializers.SerializerMethodField()
    extraction_rules = serializers.SerializerMethodField()
    file_paths = serializers.SerializerMethodField()

    class Meta:
        model = DonationBlueprint
        fields = [
            "id",
            "name",
            "description",
            "format",
            "json_extraction_root",
            "expected_fields",
            "exp_fields_regex_matching",
            "fields_to_extract",
            "file_paths",
            "extraction_rules",
            "csv_delimiter",
        ]

    def get_expected_fields(self, obj: DonationBlueprint) -> dict:
        return json.loads("[" + str(obj.expected_fields) + "]")

    def get_fields_to_extract(self, obj: DonationBlueprint) -> list:
        fields = set()
        for rule in obj.processingrule_set.all():
            if rule.comparison_operator == "":  # TODO: Check actual choice value
                fields.add(rule.field)  # which equals "Keep Field"
        return list(fields)

    def get_extraction_rules(self, obj: DonationBlueprint) -> list[dict]:
        rules = obj.processingrule_set.all().order_by("execution_order")
        return [ProcessingRuleSerializer(r).data for r in rules]

    def get_file_paths(self, obj: DonationBlueprint) -> list[dict]:
        file_paths = obj.blueprintfilepath_set.all().order_by("priority")
        return [BlueprintFilePathSerializer(fp).data for fp in file_paths]


class InstructionSerializer(serializers.ModelSerializer):
    """Serializes a DonationInstruction instance into the format expected by
    the frontend.

    see also: frontend/DDMUploader/src/types/Instruction.ts
    """

    text = serializers.SerializerMethodField()

    class Meta:
        model = DonationInstruction
        fields = ["index", "text"]

    def get_text(self, obj: DonationInstruction) -> str:
        participant_data = self.context.get("participant_data")
        return obj.render(participant_data)


class FileUploaderSerializer(serializers.ModelSerializer):
    """Serializes a FileUploader instance into the format expected by the frontend.

    see also: frontend/DDMUploader/src/types/UploaderConfig.ts
    """

    name = serializers.CharField(source="display_name")
    uploader_id = serializers.IntegerField(source="id")
    nested_zip_extraction_depth = serializers.SerializerMethodField()
    instructions = serializers.SerializerMethodField()
    blueprints = serializers.SerializerMethodField()

    class Meta:
        model = FileUploader
        fields = [
            "uploader_id",
            "upload_type",
            "nested_zip_extraction_depth",
            "name",
            "combined_consent",
            "instructions",
            "blueprints",
        ]

    def get_nested_zip_extraction_depth(self, obj: FileUploader) -> int:
        return 0 if not obj.extract_nested_zips else obj.extraction_depth

    def get_instructions(self, obj: FileUploader) -> list[dict]:
        instructions = obj.donationinstruction_set.all()
        context = {"participant_data": self.context.get("participant_data")}
        return [InstructionSerializer(i, context=context).data for i in instructions]

    def get_blueprints(self, obj: FileUploader) -> list[dict]:
        blueprints = obj.donationblueprint_set.all()
        return [BlueprintSerializer(bp).data for bp in blueprints]


class FilterConditionSerializer(serializers.ModelSerializer):
    target = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()

    class Meta:
        model = FilterCondition
        fields = [
            "index",
            "combinator",
            "condition_operator",
            "condition_value",
            "target",
            "source",
        ]

    def get_target(self, obj: FilterCondition) -> str:
        return get_filter_target_config_id(obj)

    def get_source(self, obj: FilterCondition) -> str:
        return get_filter_source_config_id(obj)


class ScalePointConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScalePoint
        fields = [
            "id",
            "index",
            "input_label",
            "heading_label",
            "value",
            "secondary_point",
        ]


class QuestionItemConfigSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    label_alt = serializers.SerializerMethodField()

    class Meta:
        model = QuestionItem
        fields = ["index", "label", "label_alt", "value", "randomize", "id"]

    def get_id(self, obj: QuestionItem) -> str:
        return f"item-{obj.id}"

    def get_label(self, obj: QuestionItem) -> str:
        return render_user_content(obj.label, self.context)

    def get_label_alt(self, obj: QuestionItem) -> str:
        return render_user_content(obj.label_alt, self.context)


class QuestionConfigSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    type = serializers.CharField(source="question_type")
    text = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    scale = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    class Meta:
        model = QuestionBase

        fields = [
            "question",
            "type",
            "page",
            "index",
            "text",
            "required",
            "items",
            "scale",
            "options",
        ]

    def get_question(self, obj: QuestionBase) -> str:
        return f"question-{obj.pk}"

    def get_text(self, obj: QuestionBase) -> str:
        return render_user_content(obj.text, self.context)

    def get_items(self, obj: QuestionBase) -> list:
        items = obj.questionitem_set.all()
        if not items:
            return []

        if obj.question_type == QuestionType.OPEN:
            # Ensure that "left-over" items are not included in config.
            if not obj.multi_item_response:
                return []

        item_configs = [
            QuestionItemConfigSerializer(i, context=self.context).data for i in items
        ]
        if obj.randomize_items:
            random.shuffle(item_configs)

        return item_configs

    def get_scale(self, obj: QuestionBase) -> list:
        scale_points = obj.scalepoint_set.all()
        return [ScalePointConfigSerializer(s).data for s in scale_points]

    def get_options(self, obj: QuestionBase) -> dict:
        if obj.question_type == QuestionType.OPEN:
            return {
                "display": obj.display,
                "input_type": obj.input_type,
                "max_input_length": obj.max_input_length,
                "multi_item_response": obj.multi_item_response,
            }

        if obj.question_type == QuestionType.MATRIX:
            return {"show_scale_headings": obj.show_scale_headings}

        return {}
