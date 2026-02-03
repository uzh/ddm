from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ddm.datadonation.models import (
    BlueprintFilePath,
    DonationBlueprint,
    DonationInstruction,
    FileUploader,
    ProcessingRule,
)
from ddm.participation.serializers import (
    FileUploaderSerializer, InstructionSerializer,
    BlueprintSerializer, ProcessingRuleSerializer,
    FilterConditionSerializer, QuestionItemConfigSerializer,
    QuestionConfigSerializer, BlueprintFilePathSerializer,
)
from ddm.projects.models import ResearchProfile, DonationProject
from ddm.questionnaire.models import (
    FilterCondition, QuestionItem, ScalePoint,
    SingleChoiceQuestion, OpenQuestion, MatrixQuestion, SemanticDifferential,
)
from ddm.questionnaire.constants import FilterSourceTypes

User = get_user_model()


class DataDonationConfigSerializersTest(TestCase):
    """One large test class for data donation config related serializers.

    One large test class is used to optimize execution time by minimizing DB
    initializations.

    Tests:
    - InstructionConfigSerializer
    - FileUploaderSerializer
    - BlueprintConfigSerializer
    - ProcessingRuleSerializer
    """

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(**{
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        })
        profile = ResearchProfile.objects.create(user=user)
        project = DonationProject.objects.create(
            name='Project', slug='base-regex-2', owner=profile)

        cls.file_uploader = FileUploader.objects.create(
            project=project,
            name='basic_file_uploader',
            display_name='basic file uploader',
            upload_type=FileUploader.UploadTypes.SINGLE_FILE,
            extract_nested_zips=True,
            extraction_depth=3,
        )

        cls.blueprint = DonationBlueprint.objects.create(
            project=project,
            name='donation_blueprint',
            display_name='donation blueprint',
            expected_fields='"a", "b"',
            file_uploader=cls.file_uploader
        )

        cls.file_path = BlueprintFilePath.objects.create(
            blueprint=cls.blueprint,
            path='some_path/file.txt',
            priority=1,
            is_regex=True,
        )

        cls.instruction = DonationInstruction.objects.create(
            text='instruction',
            index=1,
            file_uploader=cls.file_uploader
        )

        cls.rule_a = ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name='',
            field='fieldA',
            execution_order=1,
        )

        cls.rule_b = ProcessingRule.objects.create(
            blueprint=cls.blueprint,
            name='',
            field='fieldB',
            execution_order=2,
            comparison_operator=ProcessingRule.ComparisonOperators.EQUAL,
        )

    # Tests for InstructionConfigSerializer ------------------------------------
    def test_instruction_serializer(self):
        serializer = InstructionSerializer(self.instruction)

        self.assertEqual(serializer.data['text'], 'instruction')
        self.assertEqual(serializer.data['index'], 1)

    def test_instruction_serializer_with_participant_data(self):
        serializer = InstructionSerializer(
            self.instruction, context={'participant_data': {'some': 'data'}}
        )

        self.assertEqual(serializer.data['text'], 'instruction')
        self.assertEqual(serializer.data['index'], 1)

    # Tests for FileUploaderSerializer -----------------------------------------
    def test_uploader_serializer(self):
        serializer = FileUploaderSerializer(self.file_uploader)

        self.assertEqual(serializer.data['uploader_id'], self.file_uploader.id)
        self.assertEqual(serializer.data['nested_zip_extraction_depth'], 3)

        self.assertIsInstance(serializer.data['instructions'], list)
        self.assertIsInstance(serializer.data['blueprints'], list)

        self.assertEqual(len(serializer.data['instructions']), 1)
        self.assertEqual(len(serializer.data['blueprints']), 1)

        blueprint_data = serializer.data['blueprints'][0]
        extraction_rules = blueprint_data.get('extraction_rules')

        self.assertIsInstance(extraction_rules, list)
        self.assertEqual(len(extraction_rules), 2)

    def test_uploader_serializer_nested_zip_extraction_depth_when_disabled(self):
        self.file_uploader.extract_nested_zips = False
        serializer = FileUploaderSerializer(self.file_uploader)

        self.assertEqual(serializer.data['nested_zip_extraction_depth'], 0)

    # Tests for BlueprintConfigSerializer --------------------------------------
    def test_blueprint_serializer(self):
        serializer = BlueprintSerializer(self.blueprint)

        self.assertIsInstance(serializer.data['expected_fields'], list)
        self.assertEqual(len(serializer.data['expected_fields']), 2)
        self.assertIn('a', serializer.data['expected_fields'])
        self.assertIn('b', serializer.data['expected_fields'])

        self.assertIsInstance(serializer.data['fields_to_extract'], list)
        self.assertEqual(len(serializer.data['fields_to_extract']), 1)
        self.assertIn('fieldA', serializer.data['fields_to_extract'])

        self.assertIsInstance(serializer.data['extraction_rules'], list)
        self.assertEqual(len(serializer.data['extraction_rules']), 2)

        self.assertIsInstance(serializer.data['file_paths'], list)
        self.assertEqual(len(serializer.data['file_paths']), 1)

    # Tests for BlueprintFilePathSerializer ------------------------------------
    def test_blueprint_file_path_serializer(self):
        file_path = BlueprintFilePath.objects.create(
            blueprint=self.blueprint,
            path='some_path/file\.txt',
            is_regex=True,
        )
        _ = BlueprintFilePathSerializer(file_path)

    # Tests for ProcessingRuleSerializer --------------------------------------
    def test_processing_rule_serializer(self):
        _ = ProcessingRuleSerializer(self.rule_a)


class FilterConditionSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='owner2', password='123', email='owner2@mail.com'
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name='FilterProject', slug='filter-proj', owner=profile)

        cls.question_target = SingleChoiceQuestion.objects.create(
            project=cls.project, name='Target Q', variable_name='target_q',
            page=1, index=1,
        )
        cls.question_source = SingleChoiceQuestion.objects.create(
            project=cls.project, name='Source Q', variable_name='source_q',
            page=1, index=2,
        )
        cls.item_target = QuestionItem.objects.create(
            question=cls.question_target, index=1, value=1, label='Item A',
        )
        cls.item_source = QuestionItem.objects.create(
            question=cls.question_source, index=1, value=1, label='Item B',
        )

    def test_get_target_returns_question_config_id(self):
        fc = FilterCondition.objects.create(
            target_question=self.question_target,
            source_type=FilterSourceTypes.QUESTION,
            source_question=self.question_source,
            index=1,
        )
        data = FilterConditionSerializer(fc).data
        self.assertEqual(data['target'], f'question-{self.question_target.pk}')

    def test_get_target_returns_item_config_id(self):
        fc = FilterCondition.objects.create(
            target_item=self.item_target,
            source_type=FilterSourceTypes.QUESTION,
            source_question=self.question_source,
            index=1,
        )
        data = FilterConditionSerializer(fc).data
        self.assertEqual(data['target'], f'item-{self.item_target.pk}')

    def test_get_source_returns_question_config_id(self):
        fc = FilterCondition.objects.create(
            target_question=self.question_target,
            source_type=FilterSourceTypes.QUESTION,
            source_question=self.question_source,
            index=1,
        )
        data = FilterConditionSerializer(fc).data
        self.assertEqual(data['source'], f'question-{self.question_source.pk}')

    def test_get_source_returns_item_config_id(self):
        fc = FilterCondition.objects.create(
            target_question=self.question_target,
            source_type=FilterSourceTypes.QUESTION_ITEM,
            source_item=self.item_source,
            index=2,
        )
        data = FilterConditionSerializer(fc).data
        self.assertEqual(data['source'], f'item-{self.item_source.pk}')

    def test_get_source_returns_identifier_for_url_parameter(self):
        fc = FilterCondition.objects.create(
            target_question=self.question_target,
            source_type=FilterSourceTypes.URL_PARAMETER,
            source_identifier='my_param',
            index=3,
        )
        data = FilterConditionSerializer(fc).data
        self.assertEqual(data['source'], 'my_param')


class QuestionItemConfigSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='owner3', password='123', email='owner3@mail.com'
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name='ItemProject', slug='item-proj', owner=profile)

        cls.question = SingleChoiceQuestion.objects.create(
            project=cls.project, name='Q1', variable_name='q1',
            page=1, index=1,
        )
        cls.item = QuestionItem.objects.create(
            question=cls.question, index=1, value=1,
            label='Label A {{ var }}', label_alt='Label B {{ var }}',
        )

    def test_get_id_returns_prefixed_item_id(self):
        data = QuestionItemConfigSerializer(self.item, context={}).data
        self.assertEqual(data['id'], f'item-{self.item.pk}')

    def test_get_label_without_context(self):
        data = QuestionItemConfigSerializer(self.item, context={}).data
        self.assertEqual(data['label'], 'Label A')

    def test_get_label_with_context(self):
        data = QuestionItemConfigSerializer(
            self.item, context={'var': 'addendum'}).data
        self.assertEqual(data['label'], 'Label A addendum')

    def test_get_label_alt_without_context(self):
        data = QuestionItemConfigSerializer(self.item, context={}).data
        self.assertEqual(data['label_alt'], 'Label B')

    def test_get_label_alt_with_context(self):
        data = QuestionItemConfigSerializer(
            self.item, context={'var': 'addendum'}).data
        self.assertEqual(data['label_alt'], 'Label B addendum')


class QuestionConfigSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username='owner4', password='123', email='owner4@mail.com'
        )
        profile = ResearchProfile.objects.create(user=user)
        cls.project = DonationProject.objects.create(
            name='QConfigProject', slug='qconfig-proj', owner=profile)

        cls.sc_question = SingleChoiceQuestion.objects.create(
            project=cls.project, name='SC Q', variable_name='sc_q',
            page=1, index=1, text='Pick one {{ var }}',
        )
        QuestionItem.objects.create(
            question=cls.sc_question, index=1, value=1, label='Option 1',
        )
        QuestionItem.objects.create(
            question=cls.sc_question, index=2, value=2, label='Option 2',
        )
        QuestionItem.objects.create(
            question=cls.sc_question, index=3, value=3, label='Option 3',
        )


        cls.open_question = OpenQuestion.objects.create(
            project=cls.project, name='Open Q', variable_name='open_q',
            page=1, index=2, text='Type something',
            display='small', input_type='text', max_input_length=100,
            multi_item_response=False,
        )
        # Add a "left-over" item to the open question to test filtering.
        QuestionItem.objects.create(
            question=cls.open_question, index=1, value=1, label='Leftover',
        )

        cls.open_multi = OpenQuestion.objects.create(
            project=cls.project, name='Open Multi', variable_name='open_multi',
            page=1, index=3, text='Multi input',
            display='large', input_type='text',
            multi_item_response=True,
        )
        QuestionItem.objects.create(
            question=cls.open_multi, index=1, value=1, label='Multi Item',
        )

        cls.matrix_question = MatrixQuestion.objects.create(
            project=cls.project, name='Matrix Q', variable_name='matrix_q',
            page=2, index=1, text='Rate items',
            show_scale_headings=True,
        )
        QuestionItem.objects.create(
            question=cls.matrix_question, index=1, value=1, label='Row 1',
        )
        ScalePoint.objects.create(
            question=cls.matrix_question, index=1, value=1,
            input_label='Low', heading_label='Low',
        )
        ScalePoint.objects.create(
            question=cls.matrix_question, index=2, value=2,
            input_label='High', heading_label='High',
        )

    def test_get_question_returns_prefixed_pk(self):
        data = QuestionConfigSerializer(self.sc_question, context={}).data
        self.assertEqual(data['question'], f'question-{self.sc_question.pk}')

    def test_get_text_without_context(self):
        data = QuestionConfigSerializer(self.sc_question, context={}).data
        self.assertEqual(data['text'], 'Pick one')

    def test_get_text_with_context(self):
        data = QuestionConfigSerializer(
            self.sc_question, context={'var': 'fast!'}).data
        self.assertEqual(data['text'], 'Pick one fast!')

    def test_get_items_returns_items(self):
        data = QuestionConfigSerializer(self.sc_question, context={}).data
        self.assertEqual(len(data['items']), 3)

    def test_get_items_excludes_leftover_items_for_single_open(self):
        data = QuestionConfigSerializer(self.open_question, context={}).data
        self.assertEqual(data['items'], [])

    def test_get_items_includes_items_for_multi_open(self):
        data = QuestionConfigSerializer(self.open_multi, context={}).data
        self.assertEqual(len(data['items']), 1)

    def test_get_items_randomization_enable(self):
        """Verify that items are shuffled when randomize_items is True."""
        self.sc_question.randomize_items = True

        with patch('ddm.participation.serializers.random.shuffle') as mock_shuffle:
            _ = QuestionConfigSerializer(self.sc_question, context={}).data
            mock_shuffle.assert_called_once()

        self.sc_question.randomize_items = False

    def test_get_items_randomization_not_enabled(self):
        """Verify that items are shuffled when randomize_items is True."""
        self.sc_question.randomize_items = False

        with patch('ddm.participation.serializers.random.shuffle') as mock_shuffle:
            _ = QuestionConfigSerializer(self.sc_question, context={}).data
            mock_shuffle.assert_not_called()

    def test_get_scale_returns_scale_points(self):
        data = QuestionConfigSerializer(self.matrix_question, context={}).data
        self.assertEqual(len(data['scale']), 2)

    def test_get_options_for_open_question(self):
        data = QuestionConfigSerializer(self.open_question, context={}).data
        self.assertEqual(data['options']['display'], 'small')
        self.assertEqual(data['options']['input_type'], 'text')
        self.assertEqual(data['options']['max_input_length'], 100)
        self.assertFalse(data['options']['multi_item_response'])

    def test_get_options_for_matrix_question(self):
        data = QuestionConfigSerializer(self.matrix_question, context={}).data
        self.assertTrue(data['options']['show_scale_headings'])

    def test_get_options_returns_empty_dict_for_single_choice(self):
        data = QuestionConfigSerializer(self.sc_question, context={}).data
        self.assertEqual(data['options'], {})

    def test_complete_question_config_semantic_differential(self):
        question = SemanticDifferential.objects.create(
            project=self.project,
            name='Test Question',
            page=1,
            index=1,
            variable_name='test_var',
            text='Question Text',
        )
        item_a = QuestionItem.objects.create(question=question, index=1, value=1)
        item_b = QuestionItem.objects.create(question=question, index=2, value=8)
        scale_a = ScalePoint.objects.create(question=question, index=1, value=1)
        scale_b = ScalePoint.objects.create(question=question, index=2, value=6)

        expected_item_config = []
        for item in [item_a, item_b]:
            expected_item_config.append({
                'id': f'item-{item.pk}',
                'label': item.label,
                'label_alt': item.label_alt,
                'index': item.index,
                'value': item.value,
                'randomize': item.randomize,
            })
        expected_scale_config = []
        for scale_point in [scale_a, scale_b]:
            expected_scale_config.append({
                'id': scale_point.pk,
                'input_label': scale_point.input_label,
                'heading_label': scale_point.heading_label,
                'index': scale_point.index,
                'value': scale_point.value,
                'secondary_point': scale_point.secondary_point,
            })
        expected_config = {
            'question': f'question-{question.pk}',
            'type': f'{question.question_type}',
            'page': question.page,
            'index': question.index,
            'text': question.text,
            'required': question.required,
            'items': expected_item_config,
            'scale': expected_scale_config,
            'options': {}
        }

        config = QuestionConfigSerializer(question, context={}).data
        self.assertDictEqual(expected_config, config)
