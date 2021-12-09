from datetime import datetime, timedelta

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.forms.models import model_to_dict
from django.urls import reverse

from ddm.models import Question
from ddm.settings import SQ_TIMEZONE
from ddm.tools import VARIABLE_VALIDATOR


class Questionnaire(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    # Questionnaire access options:
    slug = models.SlugField(verbose_name='Questionnaire Slug')
    active = models.BooleanField(default=False)

    PUBLIC = 'public'
    TOKEN = 'token'
    ACCESS_OPTIONS = [
        (PUBLIC, 'Public'),
        (TOKEN, 'Token')
    ]
    accessibility = models.CharField(
        max_length=20,
        choices=ACCESS_OPTIONS,
        default='Public'
    )
    # TODO: Add options for tokens: Function to generate tokens

    enable_continuation = models.BooleanField(default=False)

    # Questionnaire standard values:
    missing_not_answered = models.IntegerField(
        default=-77,
        help_text=(
            'Default value if the participant does not answer '
            'the question.'
        )
    )
    missing_not_seen = models.IntegerField(
        default=-66,
        help_text=(
            'Default value if the question is not shown to the participant '
            '(e.g. because it is filtered out).'
        )
    )
    missing_invalid = models.IntegerField(
        default=-88,
        help_text=(
            'Default value if the submitted answer to a question is invalid '
            '(e.g. if the server receives a string for a question that '
            'only allows integers).'
        )
    )

    # TODO: Add Questionnaire customization options: header_logo, data processing statement

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('questionnaire-settings', args=[str(self.id)])

    def get_session_identifier(self):
        session_id = 'quest-' + str(self.pk)
        return session_id

    def get_questions(self):
        """
        Returns a set of all related questions
        """
        page_list = list(self.page_set.all().values_list('pk', flat=True))
        questions = Question.objects.filter(page__id__in=page_list)

        return questions

    def get_page_indices(self):
        """
        Returns a list containing the page indices of all related pages.
        TODO: Make sure to programmatically correct page indices to be in order to get rid of this function
        """
        return list(self.page_set.values_list('index', flat=True))

    def get_var_names(self, excluded_questions=None, excluded_externals=None,
                      excluded_triggers=None, include_external=True,
                      include_trigger=True, for_overview=False):
        """
        Returns a list of all variable names associated
        with the questionnaire.
        """
        var_names = []

        # Get the variable names of all questions and question items.
        questions = self.get_questions().order_by('page__index', 'index')

        for question in questions:
            if (excluded_questions is not None
                    and question.pk in excluded_questions):
                continue
            else:
                # Handle FileUploadQuestions.
                try:
                    file_uploads = question.fileuploaditem_set.all()
                    var_names.append(question.variable_name)
                    for fu in file_uploads:
                        var_names.append(fu.variable_name)

                except AttributeError:
                    if hasattr(question, 'variable_name'):
                        var_names.append(question.variable_name)

                        if for_overview:
                            continue

                    question_items = question.questionitem_set.all().order_by('index')
                    for item in question_items:
                        var_names.append(item.variable_name)

        # Get all variable names of associated external variables.
        if include_external:
            external_vars = self.externalvariable_set.all()
            for var in external_vars:
                if (excluded_externals is not None
                        and var.pk in excluded_externals):
                    continue
                else:
                    var_names.append(var.variable_name)

        # Get all variable names of associated trigger variables.
        if include_trigger:
            triggers = self.trigger_set.all()
            for trigger in triggers:
                if (excluded_triggers is not None
                        and trigger.pk in excluded_triggers):
                    continue
                else:
                    if hasattr(trigger, 'variable_name'):
                        var_names.append(trigger.variable_name)
                    elif hasattr(trigger, 'variable_name_stem'):
                        var_names += trigger.get_var_names()

        return var_names

    def get_var_selection_for_filter(self, target_question):
        """
        Returns a list of tuples containing (variable_name, description)
        excluding the variable names associated with a given target
        question.
        Used in the show_associated_filters() view.
        """
        var_selection = [('', '---------')]
        questions = self.get_questions().order_by('page__index', 'index')

        for question in questions:
            if question.pk == target_question.pk:
                next

            if hasattr(question, 'variable_name'):
                if isinstance(question.name, str):
                    question_name = question.name[:50]
                else:
                    question_name = question.names

                description = f'{question.variable_name}: {question_name}'
                var_selection.append((question.variable_name, description))

                try:
                    file_uploads = question.fileuploaditem_set.all()
                    for fu in file_uploads:
                        description = f'{fu.variable_name}'
                        var_selection.append((fu.variable_name, description))
                except AttributeError:
                    pass
            else:
                question_items = question.questionitem_set.all().order_by('index')
                for item in question_items:
                    if isinstance(item.answer, str):
                        item_answer = item.answer[:50]
                    else:
                        item_answer = item.answer

                    description = f'{item.variable_name}: {item_answer}'
                    var_selection.append((item.variable_name, description))

        # Get the variable names of associated external variables.
        external_vars = self.externalvariable_set.all()
        for var in external_vars:
            description = f'{var.variable_name}: {var.related_parameter}'
            var_selection.append((var.variable_name, description))

        return var_selection

    def get_submission_stats(self):
        """
        Returns a dictionary containing statistics on the submissions
        associated with the questionnaire.
        """
        # Compute submission statistics.
        submissions = self.questionnairesubmission_set.all()

        n_total = submissions.count()
        if n_total != 0:
            n_completed = submissions.filter(completed=True).count()
            completion_rate = round(n_completed / n_total * 100, 2)
        else:
            n_completed = 0
            completion_rate = None

        sub_stats = {
            'total': n_total,
            'completed': n_completed,
            'completion_rate': completion_rate
        }

        return sub_stats

    def get_missing_values(self, as_string=False):
        missing_values = []
        if as_string:
            missing_values.append(str(self.missing_not_answered))
            missing_values.append(str(self.missing_not_seen))
            missing_values.append(str(self.missing_invalid))
        else:
            missing_values.append(self.missing_not_answered)
            missing_values.append(self.missing_not_seen)
            missing_values.append(self.missing_invalid)
        return missing_values


# ----------------------------------------------------------------------
# QUESTIONNAIRE RESPONSE
# ----------------------------------------------------------------------
class QuestionnaireResponse(models.Model):
    submission = models.ForeignKey(
        'QuestionnaireSubmission',
        on_delete=models.CASCADE
    )
    variable = models.ForeignKey(
        'Variable',
        on_delete=models.PROTECT,
        null=True,
    )
    trigger = models.ForeignKey(
        'Trigger',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None
    )
    answer = models.CharField(max_length=1024)


# ----------------------------------------------------------------------
# QUESTIONNAIRE SUBMISSION
# ----------------------------------------------------------------------
class QuestionnaireSubmission(models.Model):
    class Meta:
        ordering = ['-time_started']

    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.PROTECT
    )
    session_id = models.IntegerField(unique=True)

    current_page = models.IntegerField(blank=True, null=True)
    last_submitted_page = models.IntegerField(blank=True, null=True)
    step_back = models.BooleanField(default=False)

    time_started = models.DateTimeField()
    time_submitted = models.DateTimeField(blank=True, null=True)
    completion_time = models.IntegerField(default=-99)

    completed = models.BooleanField(default=False)
    user_agent = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    access_token = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    EXPORTED_FIELDS = []

    def get_related_responses(self, submission_fields=False):
        """
        Returns a dictionary of variable_name response_value pairs.
        """
        related_responses = self.questionnaireresponse_set.all()
        response_values = {}

        for response in related_responses:
            var_name = response.variable.name
            response_values[var_name] = response.answer

        if submission_fields:
            sub_values = model_to_dict(self, exclude=['questionnaire'])
            for key in sub_values:
                response_values['sub_' + key] = sub_values[key]

        return response_values

    def close_submission(self, post_data):
        """
        Closes submission and calculates and sets final parameters.
        """
        self.time_submitted = datetime.now(tz=SQ_TIMEZONE)
        self.completed = True
        self.user_agent = post_data['user_agent'][:200]

        # Calculate time to completion.
        time_difference = self.time_submitted - self.time_started
        completion_time = time_difference / timedelta(seconds=1)
        self.completion_time = completion_time
        self.save()
        return


# ----------------------------------------------------------------------
# QUESTIONNAIRE ACCESS TOKEN
# ----------------------------------------------------------------------
class QuestionnaireAccessToken(models.Model):
    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.CASCADE
    )
    token = models.CharField(max_length=30)
    active = models.BooleanField(default=True)
    data = JSONField(null=True, blank=True)


# ----------------------------------------------------------------------
# VARIABLES
# ----------------------------------------------------------------------
class Variable(models.Model):
    name = models.CharField(max_length=24)
    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.CASCADE
    )
    related_type = models.CharField(
        max_length=10,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'questionnaire'],
                name='unique_varname_per_questionnaire'
            ),
        ]

    def __str__(self):
        return self.name


class ExternalVariable(models.Model):
    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.CASCADE
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
    STOKEN = 'token'
    SURLPARA = 'url'
    SOURCES = [
        (STOKEN, 'token'),
        (SURLPARA, 'url parameter')
    ]
    source = models.CharField(max_length=30, choices=SOURCES)
    related_parameter = models.CharField(max_length=200)
    required = models.BooleanField(default=False)
