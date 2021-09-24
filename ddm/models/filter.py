import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext as _

from ddm.models import (
    ExternalVariable, Question, QuestionItem, FileUploadItem,
    QuestionnaireResponse
)
from ddm.tools import cipher_variable, get_or_none, VARIABLE_VALIDATOR


FILTER_SEQUENCE_VALIDATOR = RegexValidator(
    r'^[0-9a-zA-Z_\)\(,\s-]*$',
    'Only alphanumeric characters, underscores, hyphens and brackets are allowed.'
)


class FilterCondition(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='filter condition name',
        validators=[VARIABLE_VALIDATOR]
    )

    # The question/question item to which the filter condition is applied.
    target_question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='filter_condition'
    )
    target_question_item = models.ForeignKey(
        'QuestionItem',
        on_delete=models.CASCADE,
        related_name='filter_condition',
        null=True,
        blank=True
    )

    # The question/question item to which the filter condition refers to.
    filter_question = models.ForeignKey(
        'Question',
        on_delete=models.SET_NULL,
        related_name='related_filter',
        null=True,
        blank=True
    )
    filter_question_item = models.ForeignKey(
        'QuestionItem',
        on_delete=models.SET_NULL,
        related_name='related_filter',
        null=True,
        blank=True
    )
    filter_upload_item = models.ForeignKey(
        'FileUploadItem',
        on_delete=models.SET_NULL,
        related_name='related_filter',
        null=True,
        blank=True
    )
    filter_ext_var = models.ForeignKey(
        'ExternalVariable',
        on_delete=models.SET_NULL,
        related_name='related_filter',
        null=True,
        blank=True
    )
    filter_variable_name = models.CharField(max_length=20)
    CQUESTION = 'question'
    CITEM = 'item'
    UITEM = 'uploaditem'
    EXVAR = 'extvar'
    COMPARISON_OBJECTS = [
        (CQUESTION, 'question'),
        (CITEM, 'item'),
        (UITEM, 'upload item'),
        (EXVAR, 'external variable')
    ]
    comparison_object = models.CharField(
        max_length=10,
        choices=COMPARISON_OBJECTS
    )

    EQUAL = 'equal'
    NOTEQUAL = 'notequal'
    BIGGER = 'bigger'
    SMALLER = 'smaller'
    COMPARISON_CHOICES = [
        (EQUAL, '='),
        (NOTEQUAL, '!='),
        (BIGGER, '>'),
        (SMALLER, '<')
    ]
    comparison_type = models.CharField(
        max_length=20,
        choices=COMPARISON_CHOICES
    )

    comparison_value = models.CharField(
        max_length=100,
        default='',
        blank=True,
        null=True
    )

    def clean(self, *args, **kwargs):
        questionnaire = self.target_question.page.questionnaire

        # Set the filter_question and filter_question_item.
        item = QuestionItem.objects.filter(
            variable_name=self.filter_variable_name,
            question__page__questionnaire=questionnaire).first()
        if item is not None:
            self.comparison_object = self.CITEM
            self.filter_question_item = item
            self.filter_question = item.question
        else:
            upload_item = FileUploadItem.objects.filter(
                variable_name=self.filter_variable_name,
                file_upload_question__page__questionnaire=questionnaire).first()

            if upload_item is not None:
                self.comparison_object = self.UITEM
                self.filter_upload_item = upload_item
                self.filter_question = upload_item.file_upload_question
            else:
                ext_variable = ExternalVariable.objects.filter(
                    variable_name=self.filter_variable_name,
                    questionnaire=questionnaire).first()
                if ext_variable is not None:
                    self.comparison_object = self.EXVAR
                    self.filter_ext_var = ext_variable

                else:
                    questions = Question.objects.filter(
                        variable__name=self.filter_variable_name,
                        page__questionnaire=questionnaire)

                    if len(questions) == 1:
                        question = questions[0]
                        self.comparison_object = self.CQUESTION
                        self.filter_question = question
                        self.filter_question_item = None
                    elif len(questions) > 1:
                        ValidationError(
                            _('More than one question matched the provided '
                              'filter_question'),
                            code='invalid'
                        )
                    else:
                        ValidationError(
                            _('No question or question item matched the provided '
                              'comparison object'),
                            code='invalid'
                        )

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def evaluate_filter(self, submission):
        """Evaluate a filter condition.

        Evaluates filter condition by first gathering the response value of the
        related filter question and then comparing this value to the filter
        condition.

        Args:
            submission (QuestionnaireSubmission): A QuestionnaireSubmission
                instance.

        Returns:
            boolean: True if condition is evaluated as true, False otherwise.
        """

        # Get the respective response value.
        if self.comparison_object == self.CQUESTION:
            var = self.filter_question.variable
        elif self.comparison_object == self.CITEM:
            var = self.filter_question_item.variable
        elif self.comparison_object == self.UITEM:
            var = self.filter_upload_item.variable
        elif self.comparison_object == self.EXVAR:
            var = self.filter_ext_var.variable
        else:
            # TODO: Catch error
            return False

        response = get_or_none(QuestionnaireResponse,
                               submission=submission, variable=var)

        if response is None:
            # TODO: raise exception
            return False

        answer = response.answer

        if hasattr(self.filter_question, 'encrypt'):
            answer = cipher_variable(answer, 'decrypt')

        if self.is_filtered(answer):
            return True
        else:
            return False

    def is_filtered(self, response_value):
        """Evaluates a filter condition for a given response value.

        Args:
            response_value (int/str): A response value.

        Returns:
            boolean: True if filter should be applied. False otherwise.
        """

        filter_condition_true = False
        int_comparison = False
        try:
            filter_value = int(self.comparison_value)
            response_value = int(response_value)
            int_comparison = True
        except:
            filter_value = self.comparison_value
            # Allow the comparison to empty string.
            if filter_value == "''" or filter_value == '""':
                filter_value = filter_value.replace("'", "")
                filter_value = filter_value.replace('"', '')
            pass

        if self.comparison_type == self.EQUAL:
            if response_value == filter_value:
                filter_condition_true = True

        elif self.comparison_type == self.NOTEQUAL:
            if response_value != filter_value:
                filter_condition_true = True

        elif int_comparison:
            if self.comparison_type == self.BIGGER:
                if response_value > filter_value:
                    filter_condition_true = True

            elif self.comparison_type == self.SMALLER:
                if response_value < filter_value:
                    filter_condition_true = True

        return filter_condition_true


class FilterSequence(models.Model):
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    question_item = models.OneToOneField(
        'QuestionItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    sequence = models.TextField(
        null=True,
        blank=True,
        validators=[FILTER_SEQUENCE_VALIDATOR]
    )

    SHOW = 'show'
    HIDE = 'hide'
    LOGIC_CHOICES = [
        (SHOW, 'show if'),
        (HIDE, 'hide if')
    ]
    logic = models.CharField(
        max_length=20,
        choices=LOGIC_CHOICES,
        default='hide'
    )

    def clean(self):
        def sequence_structure_is_valid(sequence):
            """Checks if the basic structure of the filter sequence definition
            is valid.

            Args:
                sequence (str): The filter sequence.

            Returns:
                boolean: True if structure is valid, False otherwise.
            """

            open_brackets = 0
            sequence = sequence.strip()

            for c in range(0, len(sequence)):
                if sequence[c] == '(':
                    open_brackets += 1

                    # Check if a bracket is preceded by 'AND' or 'OR'.
                    if c < 2:
                        return False
                    elif c == 2:
                        if sequence[c-2:c] != 'OR':
                            return False
                    elif (sequence[c-2:c] != 'OR' and
                          sequence[c-3:c] != 'AND'):
                        return False

                elif sequence[c] == ')':
                    open_brackets -= 1

                # Check if more brackets are closed than open.
                if open_brackets < 0:
                    return False

            return True

        def filter_conditions_exist(instance):
            """Checks if the filter conditions mentioned in the filter sequence
            actually exist.

            Args:
                instance (FilterSequence): The FilterSequence instance.

            Returns:
                boolean: True if all filter conditions exist.
                False if one or more QuestionFilters do not exist.
            """

            # Get the associated question and/or the question item.
            if instance.question is None:
                question = instance.question_item.question
                question_item = instance.question_item
            else:
                question = instance.question
                question_item = None

            # Strip logical operators from filter sequence.
            seq = instance.sequence
            seq = seq.replace('AND(', '')
            seq = seq.replace('OR(', '')
            seq = seq.replace('(', '')
            seq = seq.replace(')', '')

            # Strip whitespaces from filter sequence.
            seq = re.sub(r'\s+', '', seq, flags=re.UNICODE)

            # Get a list of the filter condition names.
            filters = seq.split(',')

            for filter_name in filters:
                q_filter = FilterCondition.objects.filter(
                    name=filter_name,
                    target_question=question,
                    target_question_item=question_item
                ).first()
                if q_filter is None:
                    return False

            return True

        super().clean()

        # Ensure that not both question and question item are None.
        if self.question is None and self.question_item is None:
            raise ValidationError(
                'Question and question_item are None, but one of them must '
                'not be None.'
            )
        # Ensure that one of question and question_item is None.
        if self.question is not None and self.question_item is not None:
            raise ValidationError(
                'Question and question_item are not None, but one of them must '
                'be None.'
            )

        # Check the filter sequence definition:
        # Check if a filter sequence has been defined.
        if not self.no_sequence_defined():
            # Check that the structure of the filter sequence is correct.
            if not sequence_structure_is_valid(self.sequence):
                error_msg = (
                    'There is something wrong with the structure of the defined '
                    'sequence. Make sure that the order of brackets is correct '
                    'and that every bracket is preceded by "AND" or "OR".'
                )
                raise ValidationError({'sequence': _(error_msg)})

            # Check if the filter conditions are referenced correctly in the
            # filter sequence.
            if not filter_conditions_exist(self):
                error_msg = (
                    'One or more of the filter conditions in the sequence do not '
                    'exist. Please make sure that only defined and saved filter '
                    'conditions are part of the filter sequence.'
                )
                raise ValidationError({'sequence': _(error_msg)})
        return

    def no_sequence_defined(self):
        """Checks if a filter sequence has been defined.

        Returns:
            boolean: True if filter sequence is empty (== ''). False otherwise.
        """

        sequence = self.sequence

        if sequence is None:
            return True
        elif re.sub(r'\s+', '', sequence, flags=re.UNICODE) == '':
            return True
        else:
            return False

    def check_if_filtered(self, submission):
        """Evaluates filter sequence and checks if the related question or
        question item must be filtered.

        Args:
            submission (QuestionnaireSubmission): QuestionnaireSubmission
                instance.

        Returns:
            boolean: True if related question should be filtered.
            False otherwise.
        """

        def evaluate_sequence(sequence, instance, submission):
            """Evaluates a filter sequence.

            Splits a filter sequence in its sub-parts (filter conditions) and
            resolves them to true or false.

            Args:
                sequence (str): The filter sequence as a string.
                instance (FilterSequence): A FilterSequence instance.
                submission (QuestionnaireSubmission): A QuestionnaireSubmission
                    instance.

            Returns:
                boolean: True if the sequence resolves to true. False otherwise.
            """

            def get_inner_expression(expression):
                """Extracts the content between the outter parantheses of an
                expression.

                Args:
                    expression (str): A part of a filter sequence.

                Returns:
                    str: A sub-part of the given expression.
                """

                inner_start = expression.find('(')
                inner_end = expression.rfind(')')
                inner = expression[inner_start + 1:inner_end]
                return inner

            def split_expression(expression):
                """Splits a given expression on commas that are not inside of
                parentheses.

                Args:
                    expression (str): A part of a filter sequence.

                Returns:
                    list: A list of sub-expressions.
                """

                open_brackets = 0
                split_indices = [0]

                for i, c in enumerate(expression):
                    if c == '(':
                        open_brackets += 1
                    elif c == ')':
                        open_brackets -= 1
                    elif c == ',' and open_brackets == 0:
                        split_indices.append(i)

                    if open_brackets < 0:
                        raise Exception('Syntax error')

                split_indices.append(len(expression))

                # Return a list of extracted sub-expressions.
                return [expression[i:j].strip(',') for i, j in zip(split_indices, split_indices[1:])]

            if '(' in sequence:
                inner_expression = get_inner_expression(sequence)

                # Split an inner expression into its direct sub-parts.
                sub_expressions = split_expression(inner_expression)

                # Evaluate all sub-expressions.
                evaluations = []
                for expr in sub_expressions:
                    evaluations.append(
                        evaluate_sequence(expr, instance, submission))

                if sequence.startswith('OR('):
                    if True in evaluations:
                        return True
                    else:
                        return False

                elif sequence.startswith('AND('):
                    if False in evaluations:
                        return False
                    else:
                        return True

            else:
                if len(sequence.split(',')) == 1:
                    if instance.question is None:
                        question = instance.question_item.question
                    else:
                        question = instance.question

                    question_item = instance.question_item

                    # Evaluate the filter condition.
                    filter_condition_name = sequence
                    f = get_or_none(
                        FilterCondition,
                        name=filter_condition_name,
                        target_question=question,
                        target_question_item=question_item
                    )
                    if f is not None:
                        return f.evaluate_filter(submission)

                else:
                    # TODO: raise exception
                    pass

        # Return False if filter sequence is not set.
        if self.no_sequence_defined():
            return False

        # Strip all whitespaces from filter sequence.
        seq = re.sub(r'\s+', '', self.sequence, flags=re.UNICODE)

        # Evaluate the filter sequence.
        seq_evaluation = evaluate_sequence(seq, self, submission)

        # Interpret filter evaluation according to the set filter logic.
        if self.logic == self.SHOW:
            if seq_evaluation is True:
                filter_out = False
            else:
                filter_out = True
        elif self.logic == self.HIDE:
            if seq_evaluation is True:
                filter_out = True
            else:
                filter_out = False

        return filter_out
