import json
import random

from ckeditor.fields import RichTextField

from datetime import datetime

from django.core import serializers
from django.core.validators import RegexValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

from polymorphic.models import PolymorphicModel

# Here, to avoid circular dependency errors, a general import is used instead of
# an explicit import.
import ddm.models as ddm_models
from ddm.tools import cipher_variable, get_or_none, VARIABLE_VALIDATOR


FILE_TYPE_VALIDATOR = RegexValidator(
    r'^(\s*\.[0-9a-zA-Z]*;*)*$',
    ('File types must be separated by a semicolon (;) and must be of the form'
     '".filename", where the filename can only contain letters and numbers.')
)


class Question(PolymorphicModel):
    page = models.ForeignKey(
        'Page',
        on_delete=models.CASCADE,
        blank=True
    )
    name = models.CharField(max_length=255)
    question_text = RichTextField(null=True, blank=True)
    question_instruction = RichTextField(null=True, blank=True)
    required = models.BooleanField(default=False)

    TYPE_GENERIC = 'genericquestion'
    TYPE_SC = 'singlechoicequestion'
    TYPE_MC = 'multichoicequestion'
    TYPE_MATRIX = 'matrixquestion'
    TYPE_DIFFERENTIAL = 'differentialquestion'
    TYPE_LIST = 'listquestion'
    TYPE_TRANSITION = 'transitionquestion'
    TYPE_OPEN = 'openquestion'
    TYPE_FILE_UL = 'fileuploadquestion'
    TYPE_FILE_FEEDBACK = 'filefeedback'
    QUESTION_TYPES = [
        (TYPE_GENERIC, 'Generic'),
        (TYPE_SC, 'Single Choice'),
        (TYPE_MC, 'Multi Choice'),
        (TYPE_MATRIX, 'Matrix'),
        (TYPE_DIFFERENTIAL, 'Differential'),
        (TYPE_LIST, 'List'),
        (TYPE_TRANSITION, 'Transition'),
        (TYPE_OPEN, 'Open'),
        (TYPE_FILE_UL, 'File Upload'),
        (TYPE_FILE_FEEDBACK, 'File Feedback')
    ]
    DEFAULT_QUESTION_TYPE = TYPE_GENERIC
    question_type = models.CharField(
        max_length=44,
        blank=False,
        choices=QUESTION_TYPES,
        default=DEFAULT_QUESTION_TYPE
    )

    index = models.PositiveIntegerField(default=1)

    variable = models.OneToOneField(
        'Variable',
        on_delete=models.PROTECT,
        null=True,
    )

    class Meta:
        ordering = ['page__index', 'index']

    def __init__(self, *args, **kwargs):
        kwargs['question_type'] = self.DEFAULT_QUESTION_TYPE
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        view_name = self.question_type + '-update'
        return reverse(view_name,
                       kwargs={'pk': self.pk, 'q': self.page.questionnaire.pk})

    def get_admin_url(self):
        view_name = 'admin:{}_{}_change'.format(self._meta.app_label,
                                                self._meta.model_name)
        return reverse(view_name, args=(self.id,))

    def save(self, *args, **kwargs):
        page = self.page
        q_on_page = page.question_set.all()

        if not self.pk:
            # Set index to max index on page + 1.
            q_indices = q_on_page.values_list('index', flat=True)
            if len(q_indices) > 0:
                max_index = max(q_indices)
                self.index = max_index + 1
            else:
                self.index = 1

        else:
            q_indices = q_on_page.exclude(pk=self.pk).values_list('index',
                                                                  flat=True)

            if self.index in q_indices:
                self.index = max(q_indices) + 1

        super().save(*args, **kwargs)

    def super_create_question_response(self, post_data, response_type,
                                       valid_responses, default_response):
        """Validates the question responses in a POST request.

        Validates posted responses for all variables associated with a question.

        Args:
            post_data (django.http.QueryDict): The POST data retrieved from a
                request instance.
            response_type (str): Accepted type of the response in the post data.
                Either 'int' for a numeric response or 'str' for a string
                response.
            valid_responses (list): A list of valid responses. Can also be an
                empty list, e.g. when response_type == 'str'.
            default_response (str/int): Default response value.

        Returns:
            list: A list of dictionaries containing the validated response data.
            Each dictionary relates to a variable that is associated with
            the question. The dictionaries have the following structure:

            {'var_name': var_name,
             'value': response}
        """

        # Add the value for 'missing_not_seen' defined on the Questionnaire
        # level to the list of valid responses.
        valid_responses.append(self.page.questionnaire.missing_not_seen)

        # Questionnaire specific values for invalid and or blank responses.
        invalid_value = self.page.questionnaire.missing_invalid
        not_answered = self.page.questionnaire.missing_not_answered

        question_responses = []

        # Check if question responses must be encrypted before the validation.
        if hasattr(self, 'encrypt'):
            encrypt = self.encrypt
        else:
            encrypt = False

        # Validation of responses that relate to a Question-level variable.
        if hasattr(self, 'variable_name'):

            if self.variable_name in post_data:
                if response_type == 'int':
                    response = int(post_data[self.variable_name])

                    if response not in valid_responses:
                        response = invalid_value

                else:
                    response = post_data[self.variable_name]
                    if response == '':
                        response = default_response

                    if encrypt:
                        response = cipher_variable(response, 'encrypt')

            else:
                response = not_answered

            question_responses.append({
                'var_name': self.variable_name,
                'value': response
            })

        # Validation of responses that relate to QuestionItem-level variables.
        items = self.questionitem_set.values_list('variable_name', flat=True)
        for var_name in items:
            if var_name in post_data:
                if response_type == 'int':
                    response = int(post_data[var_name])

                    # Check if the response value is valid.
                    if response not in valid_responses:
                        response = invalid_value

                else:
                    response = post_data[var_name]
                    if encrypt:
                        response = cipher_variable(response, 'encrypt')

            else:
                response = default_response

            question_responses.append({
                'var_name': var_name,
                'value': response
            })

        return question_responses

    def get_saved_responses(self, submission):
        """Get the saved responses related to the question from a submission
        instance.

        Args:
            submission (QuestionnaireSubmission): A QuestionnaireSubmission
                instance from which the saved responses are retrieved.

        Returns:
            dict: A dictionary containing the saved responses.
            The keys are the variable names and the respective responses
            are stored as values.
        """

        def get_response_value(obj, submission, decrypt=False):
            existing_response = ddm_models.QuestionnaireResponse.objects.filter(
                submission=submission,
                variable=obj.variable).first()

            if existing_response is not None:
                value = existing_response.answer

                if decrypt:
                    value = cipher_variable(value, 'decrypt')
                return value

            else:
                return None

        saved_responses = {}

        if hasattr(self, 'encrypt'):
            decrypt = self.encrypt
        else:
            decrypt = False

        if hasattr(self, 'variable_name'):
            response_value = get_response_value(self, submission, decrypt)

            if response_value is not None:
                if isinstance(self, OpenQuestion):
                    missing_values = self.page.questionnaire.get_missing_values(as_string=True)
                    if response_value in missing_values:
                        response_value = ''

                saved_responses[self.variable_name] = response_value

        item_set = self.questionitem_set.all()
        for item in item_set:
            response_value = get_response_value(item, submission, decrypt)

            if response_value is not None:
                saved_responses[item.variable_name] = response_value

        # TODO: Add extra rule for FileUploadQuestion

        return saved_responses

    def get_filtered_variable_names(self, submission):
        """Get the names of the variables related to the question that are
        filtered out.

        Args:
            submission (QuestionnaireSubmission): The submission for which the
                filtering should be checked.

        Returns:
            list: A list containing the names of the variables that are
            filtered out.
        """

        filtered_out = []

        # 1: Check filters that are associated with the question.
        f_seq_question = get_or_none(ddm_models.FilterSequence,
                                     question=self, question_item=None)

        if f_seq_question is not None:

            if f_seq_question.check_if_filtered(submission) is True:
                if self.variable is None:
                    variable_name = 'q-' + str(self.pk)
                else:
                    variable_name = self.variable.name

                filtered_out.append(variable_name)

        # 2: Check filters that are associated with the question items.
        item_set = self.questionitem_set.all()
        for item in item_set:
            f_seq_item = get_or_none(
                ddm_models.FilterSequence,
                question_item=item
            )

            if f_seq_item is not None:
                if f_seq_item.check_if_filtered(submission) is True:
                    variable_name = item.variable.name
                    filtered_out.append(variable_name)

        return list(set(filtered_out))

    def get_response_variables(self, var_form='regular'):
        """Get the names of the response variables associated with this
        question.

        Args:
            var_form (str): Can either be 'regular' or 'template'
                (default: 'regular').
                'regular' returns the variable names
                as defined in the Question or QuestionItem instances.
                'template' returns the variables names in the form
                "'q-' + str(Question.pk)" or "'qi-' + str(QuestionItem.pk)".

        Returns:
            list: A list containing the names of variables associated to the
            question.
        """

        response_variables = []
        if var_form not in ['regular', 'template']:
            # TODO: raise error for a disallowed value has been entered for var_form.
            pass

        if hasattr(self, 'variable_name'):
            if var_form == 'regular':
                response_variables.append(self.variable_name)
            elif var_form == 'template':
                response_variables.append('q-' + str(self.pk))

        else:
            item_set = self.questionitem_set.all()
            for item in item_set:
                if var_form == 'regular':
                    response_variables.append(item.variable_name)
                elif var_form == 'template':
                    response_variables.append('qi-' + str(item.pk))

        return response_variables

    def get_ordered_items(self):
        """Creates a list of the QuestionItems that are associated to a
        question.

        Returns:
            list: A list of QuestionItems that belong to the question.
            Generally, the QuestionItems in this list are in ascending order
            according to their index. QuestionItems that are defined to be
            displayed in a random order, are randomly placed around those items
            that should not be placed randomly.
        """

        items = self.questionitem_set.all()
        ordered_items = [None] * len(items)
        random_items = []

        # Gather non-randomized and randomized items separately.
        for item in items:
            if item.randomize:
                random_items.append(item)
            else:
                ordered_items[item.index-1] = item

        # Arrange randomized items around the fixed items.
        for item in random_items:
            open_indices = [i for i, x in enumerate(ordered_items) if x is None]
            ordered_items[random.choice(open_indices)] = item

        return ordered_items


class TransitionQuestion(Question):
    DEFAULT_QUESTION_TYPE = Question.TYPE_TRANSITION

    def create_question_response(self, post_data):
        return []


class SingleChoiceQuestion(Question):
    DEFAULT_QUESTION_TYPE = Question.TYPE_SC

    variable_name = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )

    def create_question_response(self, post_data):
        response_type = 'int'
        valid_responses = list(self.questionitem_set.values_list('value',
                                                                 flat=True))
        default_response = self.page.questionnaire.missing_not_answered
        question_response = self.super_create_question_response(
            post_data=post_data,
            valid_responses=valid_responses,
            response_type=response_type,
            default_response=default_response
        )
        return question_response


class OpenQuestion(Question):
    DEFAULT_QUESTION_TYPE = Question.TYPE_OPEN

    variable_name = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )

    encrypt = models.BooleanField(default=False)

    SMALL = 'small'
    LARGE = 'large'
    DISPLAY_TYPES = [
        (SMALL, 'small'),
        (LARGE, 'large'),
    ]
    display_size = models.CharField(
        max_length=10,
        blank=False,
        choices=DISPLAY_TYPES,
        default='small'
    )

    DATE = '[^0-9\.]+'
    NUMBER = '[^0-9]+'
    TEXT = 'text'
    FORMATS = [
        (DATE, 'date'),
        (NUMBER, 'number'),
        (TEXT, 'text')
    ]
    input_format = models.CharField(
        max_length=220,
        blank=False,
        choices=FORMATS,
        default='text'
    )

    max_input_length = models.IntegerField(
        blank=True,
        null=True
    )

    def create_question_response(self, post_data):
        response_type = 'str'
        valid_responses = []
        default_response = str(self.page.questionnaire.missing_not_answered)
        question_response = self.super_create_question_response(
            post_data=post_data,
            valid_responses=valid_responses,
            response_type=response_type,
            default_response=default_response
        )
        return question_response


class MultiChoiceQuestion(Question):
    DEFAULT_QUESTION_TYPE = Question.TYPE_MC

    def create_question_response(self, post_data):
        response_type = 'int'
        valid_responses = [0, 1]
        default_response = 0
        question_responses = self.super_create_question_response(
            post_data=post_data,
            valid_responses=valid_responses,
            response_type=response_type,
            default_response=default_response
        )
        return question_responses


class MatrixQuestion(Question):
    DEFAULT_QUESTION_TYPE = Question.TYPE_MATRIX

    scale_repetition = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=0,
        help_text='Repeat scale every x lines.'
    )

    def create_question_response(self, post_data):
        response_type = 'int'
        valid_responses = list(
            self.questionscale_set.values_list('value', flat=True))
        default_response = self.page.questionnaire.missing_not_answered
        question_responses = self.super_create_question_response(
            post_data=post_data,
            valid_responses=valid_responses,
            response_type=response_type,
            default_response=default_response
        )
        return question_responses


class DifferentialQuestion(Question):
    DEFAULT_QUESTION_TYPE = Question.TYPE_DIFFERENTIAL

    scale_points = models.PositiveIntegerField(
        default=5,
        help_text='The maximum number of scale points is 9.',
        validators=[
            MaxValueValidator(9)
        ]
    )

    def create_question_response(self, post_data):
        response_type = 'int'
        valid_responses = list(range(1, self.scale_points + 1))
        default_response = self.page.questionnaire.missing_not_answered
        question_responses = self.super_create_question_response(
            post_data=post_data,
            valid_responses=valid_responses,
            response_type=response_type,
            default_response=default_response
        )
        return question_responses


class ListQuestion(Question):
    DEFAULT_QUESTION_TYPE = Question.TYPE_LIST

    encrypt = models.BooleanField(
        default=False,
        help_text=('If on, the input is stored in the database in an encrypted '
                   'form, and not as plain input. If the variable is '
                   'referenced in a text or description within the '
                   'questionnaire, the tag "|decrypt" must be added '
                   '(e.g. [[ var_name|decrypt ]]), otherwise '
                   'the encrypted value will be displayed.')
    )

    def create_question_response(self, post_data):
        response_type = 'str'
        valid_responses = []
        default_response = self.page.questionnaire.missing_not_answered
        question_responses = self.super_create_question_response(
            post_data=post_data,
            valid_responses=valid_responses,
            response_type=response_type,
            default_response=default_response
        )
        return question_responses


class FileUploadQuestion(Question):
    DEFAULT_QUESTION_TYPE = Question.TYPE_FILE_UL

    SF = 'singlefile'
    ZIP = 'zipfile'
    UPLOAD_MODES = [
        (SF, 'Single File'),
        (ZIP, '.zip File'),
    ]
    upload_mode = models.CharField(
        blank=False,
        null=False,
        default=SF,
        choices=UPLOAD_MODES,
        max_length=20
    )

    max_filesize = models.IntegerField(
        verbose_name='filesize in kb',
        default=100000
    )

    requires_consent = models.BooleanField(
        default=False
    )

    variable_name = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )

    def create_question_response(self, post_data):
        response_type = 'str'
        valid_responses = []
        default_response = str(self.page.questionnaire.missing_not_answered)
        question_response = self.super_create_question_response(
            post_data=post_data,
            valid_responses=valid_responses,
            response_type=response_type,
            default_response=default_response
        )
        return question_response


class FileUploadItem(models.Model):
    file_upload_question = models.ForeignKey(
        'FileUploadQuestion',
        on_delete=models.CASCADE,
        null=True
    )

    variable_name = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )
    variable = models.OneToOneField(
        'Variable',
        on_delete=models.PROTECT,
        null=True,
    )

    expected_filename = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text=(
            'Optional: Specify the name of the uploaded file. '
            'Leave empty if the file contents should be matched without '
            'checking the file name. If multiple filenames should be accepted, '
            'separate the filenemas with a semicolon (;). '
            'Currently only applicable to zip uploads.'
        )
    )
    valid_file_types = models.CharField(
        max_length=100,
        help_text=(
            'Indicate all valid file types, separated by semicolons '
            '(e.g. .json; .xlsx). Currently, only .json files '
            'are supported.'
        ),
        validators=[FILE_TYPE_VALIDATOR]
    )
    max_filesize = models.IntegerField(
        verbose_name='filesize in kb',
        default=100000
    )
    validation_fields = models.TextField(
        help_text=(
            'List all fields that must be included in the uploaded '
            'file, separated by semicolons (e.g. name; date; ...). '
            'This serves as a file validation, and the upload will be '
            'aborted if the file does not include at least the listed '
            'fields.'
        )
    )
    extraction_fields = models.TextField(
        help_text=(
            'List all fields that shall be extracted from the uploaded '
            'file, separated by semicolons (e.g. name; date; ...). '
            'Only the fields listed here will be stored in the '
            'database.'
        )
    )

    endpoint = 'file-processor'

    def get_valid_file_types(self):
        """Extracts a list of valid file types from a string of file types.
        """
        valid_types = self.valid_file_types.replace(' ', '')
        valid_types = valid_types.replace('\n', '')
        valid_types = valid_types.replace('.', '')
        valid_types = valid_types.split(';')
        return valid_types

    @staticmethod
    def get_field_names(field_string):
        """Extracts a list of field names from a string of field names.
        """
        field_names = [x.strip(' ') for x in field_string.split(';')]
        return field_names

    def check_filetype(self, file_content_type):
        """Checks if a given file content type is valid according to the
        settings of the FileUploadItem instance.

        Args:
            file_content_type (str): The content type of an uploaded file.

        Returns:
            str/None: If the file content type is valid, returns the name of the
            file content type. Returns None if it is invalid.
        """

        file_type = file_content_type.replace('.', '').split('/')[-1]

        if file_type in self.get_valid_file_types():
            return file_type
        else:
            return None

    @staticmethod
    def get_file_content(file, file_type):
        """Get the content of a file.

        Args:
            file (Any): The uploaded file.
            file_type (str): The type of the file.

        Returns:
            Any: The read content of the provided file.
        """

        raw_content = file.read()

        if file_type == 'json':
            file_content = json.loads(raw_content.decode('utf-8'))
        else:
            file_content = None

        return file_content

    def fields_are_valid(self, file_content):
        """Check if the fields contained in an uploaded file match the expected
        fields.
        """

        valid_fields = self.get_field_names(self.validation_fields)

        if len(file_content) > 0:
            if set(valid_fields).issubset(list(file_content[0].keys())):
                return True
            else:
                return False
        else:
            return True

    def extract_data(self, file_content):
        """Extract the data from an uploaded file.

        Args:
            file_content (): _

        Returns:
            str: Extracted data as a json-formatted string.
        """

        fields_to_extract = self.get_field_names(self.extraction_fields)
        data = []

        if len(file_content) > 0:
            data = [{f: r.get(f, 'NA') for f in fields_to_extract} for r in file_content]
        else:
            data_row = {'status': 'no data in file'}
            data.append(data_row)

        extracted_data = json.dumps(data)
        return extracted_data

    def export_data(self):
        """Export the uploaded data associated to this FileUploadItem as JSON.

        Returns:
            Uploaded data in JSON format.
        """

        questionnaire = self.file_upload_question.page.questionnaire

        # Get all submissions.
        submissions = ddm_models.QuestionnaireSubmission.objects.filter(
            questionnaire=questionnaire)
        variable = ddm_models.Variable.objects.get(
            questionnaire=questionnaire, name=self.variable_name)

        # Get all associated upload ids.
        upload_ids = ddm_models.QuestionnaireResponse.objects.filter(
            submission__in=submissions, variable=variable).values_list(
            'answer', flat=True)

        data = ddm_models.UploadedData.objects.filter(upload_id__in=upload_ids)
        data = serializers.serialize('json', data)
        return data


class FileFeedback(Question):
    """
    TODO: Should add further restrictions to this type of question:
    1. must be on a page > page related_filequestion (also cannot be on the same page)
    2. if need_to_confirm input must be required (include specific validation error for this question type)
    """
    DEFAULT_QUESTION_TYPE = Question.TYPE_FILE_FEEDBACK

    variable_name = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )

    # TODO: Rename, as this name is no longer accurate
    related_filequestion = models.ForeignKey(
        'FileUploadItem',
        on_delete=models.CASCADE
    )
    need_to_confirm = models.BooleanField(default=False)
    display_upload_table = models.BooleanField(default=False)
    display_upload_stats = models.BooleanField(default=False)

    def create_question_response(self, post_data):
        response_type = 'int'
        valid_responses = [0, 1]
        default_response = self.page.questionnaire.missing_not_answered
        question_response = self.super_create_question_response(
            post_data=post_data,
            valid_responses=valid_responses,
            response_type=response_type,
            default_response=default_response
        )
        return question_response

    def get_table_data(self, submission):
        """
        TODO: Add function description.
        """
        related_fq = self.related_filequestion

        upload = get_or_none(ddm_models.QuestionnaireResponse,
                             submission=submission,
                             variable=related_fq.variable)

        if upload is not None:
            upload_id = upload.answer

            raw_data = get_or_none(ddm_models.UploadedData, upload_id=upload_id)

            if raw_data is None:
                table_fields = ['Response']
                file_data_list = [['No Data Extracted.']]
            else:
                json_data = raw_data.data
                file_data_list = [list(row.values()) for row in json_data]
                if len(json_data) == 0:
                    table_fields = ['Response']
                    file_data_list = [['No Data Extracted.']]
                else:
                    table_fields = [k for k in json_data[0].keys()]

        else:
            table_fields = ['Response']
            file_data_list = [['No Data Extracted.']]

        table_data = {
            'table_fields': table_fields,
            'data': file_data_list
        }
        return table_data

    def check_confirmation(self, submission):
        """Check if the respondent has confirmed the upload of his*her data.

        Args:
            submission (QuestionnaireSubmission): A QuestionnaireSubmission
                instance.

        Returns:
            boolean: Returns True if respondent has confirmed the upload or
            if no confirmation is needed and False if respondent did not
            confirm.
        """

        if not self.need_to_confirm:
            return True

        confirmation = ddm_models.QuestionnaireResponse.objects.filter(
            submission=submission,
            variable__name=self.variable_name
        ).first()

        if str(confirmation.answer) == '1':
            return True
        elif str(confirmation.answer) == '0':
            return False
        else:
            return False

    def get_upload_id(self, submission):
        """Get the uploaded id stored in a submission.

        Args:
            submission (QuestionnaireSubmission): A QuestionnaireSubmission
                instance.

        Returns:
            str/None: Returns the upload id in form of a string or None if no
            upload id has been created.
        """

        var_name = self.related_filequestion.variable_name
        related_response = ddm_models.QuestionnaireResponse.objects.filter(
            submission=submission,
            variable__name=var_name
        ).first()

        if related_response is not None:
            upload_id = related_response.answer
        else:
            upload_id = None

        return upload_id

    def update_data_entries(self, submission):
        """
        TODO: Better description of this function.
        Update data entries.
        Keep if confirmed, mark for deletion if not confirmed.
        """
        upload_id = self.get_upload_id(submission)

        # Check if upload needed to be confirmed.
        if self.need_to_confirm:
            has_confirmed = self.check_confirmation(submission)

            if not has_confirmed and upload_id is not None:
                # Delete uploaded data and delete related UploadedDataTemp instance.
                uploaded_data = get_or_none(ddm_models.UploadedData,
                                            upload_id=upload_id)
                if uploaded_data is not None:
                    uploaded_data.delete()

        # In any case, delete data temp entry.
        if upload_id is not None:
            temp_entry = get_or_none(ddm_models.UploadedDataTemp,
                                     upload_id=upload_id)
            if temp_entry is not None:
                temp_entry.delete()

        return


# ----------------------------------------------------------------------
# QUESTION ITEM
# ----------------------------------------------------------------------
class QuestionItem(models.Model):
    class Meta:
        ordering = ['index']

    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE
    )
    answer = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    answer_alt = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Additional Answer'
    )
    variable_name = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )
    variable = models.OneToOneField(
        'Variable',
        on_delete=models.PROTECT,
        null=True,
    )
    index = models.IntegerField()
    value = models.IntegerField()
    randomize = models.BooleanField(default=False)


# ----------------------------------------------------------------------
# QUESTION SCALE
# ----------------------------------------------------------------------
class QuestionScale(models.Model):
    class Meta:
        ordering = ['index']

    question = models.ForeignKey(
        'MatrixQuestion',
        on_delete=models.CASCADE
    )
    index = models.IntegerField()
    label = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    value = models.IntegerField()
    add_border = models.BooleanField(
        default=False
    )
