import random

from ckeditor.fields import RichTextField
from django.db import models
from django.urls import reverse
from polymorphic.models import PolymorphicModel

# Here, to avoid circular dependency errors, a general import is used instead of
# an explicit import.
import ddm.models as ddm_models
from ddm.tools import cipher_variable, get_or_none, VARIABLE_VALIDATOR


class QuestionBase(PolymorphicModel):
    project = models.ForeignKey(
        ddm_models.DonationProject,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    question_text = RichTextField(null=True, blank=True)
    question_instruction = RichTextField(null=True, blank=True)

    required = models.BooleanField(default=False)

    TYPE_GENERIC = 'generic-question'
    TYPE_SC = 'singlechoice-question'
    TYPE_MC = 'multichoice-question'
    TYPE_MATRIX = 'matrix-question'
    TYPE_DIFFERENTIAL = 'differential-question'
    TYPE_LIST = 'list-question'
    TYPE_TRANSITION = 'transition-question'
    TYPE_OPEN = 'open-question'
    QUESTION_TYPES = [
        (TYPE_GENERIC, 'Generic'),
        (TYPE_SC, 'Single Choice'),
        (TYPE_MC, 'Multi Choice'),
        (TYPE_MATRIX, 'Matrix'),
        (TYPE_DIFFERENTIAL, 'Differential'),
        (TYPE_LIST, 'List'),
        (TYPE_TRANSITION, 'Transition'),
        (TYPE_OPEN, 'Open'),
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
        ordering = ['index']

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


class SingleChoiceQuestionAlt(QuestionBase):
    DEFAULT_QUESTION_TYPE = QuestionBase.TYPE_SC

    variable_name = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )

    """
    items = [
        {'label': String, 'value': Integer, 'index': Integer, 'random': Boolean}
    ]
    result = {'question': Question.pk, 'answer': Integer (item value)}
    """

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