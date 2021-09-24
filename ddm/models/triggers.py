import json
import random

from datetime import datetime, timedelta

from django.contrib.postgres.fields import JSONField
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import models
from django.urls import reverse

from polymorphic.models import PolymorphicModel

from ddm.models import (
    Variable, QuestionnaireResponse, QuestionnaireAccessToken, UploadedData,
    UploadedDataTemp, FileFeedback
)
from ddm.settings import SQ_TIMEZONE
from ddm.tools import (
    fill_variable_placeholder, generate_id, get_or_none, VARIABLE_VALIDATOR
)


class Trigger(PolymorphicModel):
    """
    Triggers can be used to execute certain actions when a questionnaire page is
    requested or posted.

    Attributes:
        name (str): Can either be 'regular' or 'template' (default: 'regular').
        questionnaire (Questionnaire): The questionnaire in in which the trigger
            will be executed.
        execution_page (Page): The page on which the trigger will be executed.
        execution_point (str): At which point the trigger will be exectued.
            Either 'before' (i.e., when the Page is requested)
            or 'after' (i.e., when the Page is posted).
        trigger_type (str): The type of the trigger. Must be one of the following:
            'tokengenerator': Generates an access token for another
                questionnaire on execution.
            'variablesfromdata': Generates and populates a new variable based on
                some provided data on execution.
            'emailtrigger': A trigger that will send out an e-mail at a
                predefined point in time to a defined receiver.
            'cleanuploaddata': Cleans some data that has been uploaded by a
                participant on execution.

    """
    name = models.CharField(max_length=50)
    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.CASCADE
    )
    execution_page = models.ForeignKey(
        'Page',
        on_delete=models.CASCADE
    )

    EXECUTE_BEFORE = 'before'
    EXECUTE_AFTER = 'after'
    EXECUTION_POINTS = [
        (EXECUTE_BEFORE, 'before'),
        (EXECUTE_AFTER, 'after')
    ]
    execution_point = models.CharField(
        max_length=20,
        choices=EXECUTION_POINTS
    )

    TYPE_TOKEN_GENERATOR = 'tokengenerator'
    TYPE_VAR_FROM_DATA = 'variablesfromdata'
    TYPE_EMAIL = 'emailtrigger'
    TYPE_CLEAN_UL_DATA = 'cleanuploaddata'
    TRIGGER_TYPES = [
        (TYPE_TOKEN_GENERATOR, 'Token Generator'),
        (TYPE_VAR_FROM_DATA, 'Variables from Data'),
        (TYPE_EMAIL, 'E-Mail Trigger'),
        (TYPE_CLEAN_UL_DATA, 'Clean Upload Data')
    ]
    DEFAULT_TRIGGER_TYPE = None
    trigger_type = models.CharField(
        max_length=44,
        blank=False,
        null=False,
        choices=TRIGGER_TYPES
    )

    def __init__(self, *args, **kwargs):
        kwargs['trigger_type'] = self.DEFAULT_TRIGGER_TYPE
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        view_name = self.trigger_type + '-update'
        return reverse(view_name, args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.trigger_type = self.DEFAULT_TRIGGER_TYPE

        super().save(*args, **kwargs)


class TokenGenerator(Trigger):
    """
    A generator that on execution creates a token to be used to get access to a
    questionnaire. Optionally, answer data from the current participant can
    be attached to this token.

    Attribute:
        target (Questionnaire): The questionnaire for which the access token
            should be valid.
        store_in_response (bool): If true, the token will be stored in the
            response data of the participant.
        variable_name (str): The identifying name of the variable in which the
            token will be stored in a participants responses. Must be unique for
            the questionnaire, in which the trigger is executed.
        variable (Variable): The variable object to which the variable_name will
            be linked. Automatically created/updated when the trigger is saved.
        included_vars (str): A string that contains all variables for which the
            stored data should be associated to the token. Multiple variables
            should be separated by commas ('Var_1, Var_2, Var_3').
        include_session_id (bool): If True, the session id of the participant
            that is currently filling out the questionnaire is also attached to
            the token.
    """
    DEFAULT_TRIGGER_TYPE = Trigger.TYPE_TOKEN_GENERATOR

    target = models.ForeignKey(
        'Questionnaire',
        on_delete=models.CASCADE
    )
    # TODO for later: Add option to specify a token_format.

    store_in_response = models.BooleanField(default=True)
    variable_name = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )
    variable = models.OneToOneField(
        'variable',
        on_delete=models.PROTECT,
        null=True,
    )
    included_vars = models.TextField(
        max_length=500,
        null=True,
        blank=True
    )

    include_session_id = models.BooleanField(default=False)

    def execute(self, sub):
        """
        Generates a unique token and associates it with the specified target
        questionnaire.
        """
        # Generate a token that is unique for the target questionnaire.
        token = generate_id(8, letters=True, numbers=True)
        existing_tokens = self.target.questionnaireaccesstoken_set.all()
        existing_tokens_list = existing_tokens.values_list('token', flat=True)
        while token in existing_tokens_list:
            token = generate_id(8, letters=True, numbers=True)

        # Get the values of all variables to be included in the token data.
        variables = [x.strip() for x in self.included_vars.split(',')]
        var_dict = {}
        for var in variables:
            value = None
            var = Variable.objects.filter(
                name=var,
                questionnaire=sub.questionnaire
            ).first()

            if var is not None:
                response = QuestionnaireResponse.objects.get(
                    variable=var,
                    submission=sub
                )

                value = response.answer

            if value is not None:
                var_dict[var] = value

        if self.include_session_id:
            var_dict['int_session_id'] = sub.session_id

        # Save the token and the associated data for the target questionnaire.
        qat = QuestionnaireAccessToken(
            questionnaire=self.target,
            token=token,
            data=var_dict
        )
        qat.save()

        if self.store_in_response:
            qr = QuestionnaireResponse.objects.filter(
                submission=sub,
                variable=self.variable
            ).first()

            if qr is None:
                qr = QuestionnaireResponse(
                    submission=sub,
                    variable=self.variable
                )

            qr.answer = token
            qr.save()

        return


class VariablesFromData(Trigger):
    """
    Takes values from the data a participant uploaded/donated and stores them in
    variables that are saved in the response of the participant.
    Currently extracts n random entries of the field defined in
    'field_to_extract' and stores them in variables following the form
    variable_name_stem_1 ... variable_name_Stem_n.

    Attributes:
        related_upload_question (FileUploadItem): The FileUploadItem that
            contains the relevant data.
        variable_name_stem (str): The stem of the variable name as which the
            extracted data should be stored.
        variable_name_stem_prev (str): Helper attribute to be able to alter the
            variable_name_stem.
        n_variables (int): The number of entries that should be extracted from
            the uploaded data.
        n_variables_prev (int): Helper attribute to be able to alter
            n_variables.
        field_to_extract (str): The field of the uploaded data from which the
            based on which the variables will be created.
        filter_active (bool):
        filter_condition (str):
    """
    DEFAULT_TRIGGER_TYPE = Trigger.TYPE_VAR_FROM_DATA

    # TODO: Change this to related_upload_item which is clearer and actually correct.
    related_upload_question = models.ForeignKey(
        'FileUploadItem',
        on_delete=models.CASCADE
    )

    variable_name_stem = models.CharField(
        max_length=20,
        validators=[VARIABLE_VALIDATOR]
    )
    variable_name_stem_prev = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    n_variables = models.IntegerField()
    n_variables_prev = models.IntegerField(blank=True, null=True)

    field_to_extract = models.CharField(max_length=255)

    # TODO: Check if these two attributes are necessary.
    filter_active = models.BooleanField(default=False)
    filter_condition = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Keep track of changes in the variable name stem
        """
        if self.pk:
            obj = VariablesFromData.objects.get(pk=self.pk)
            self.variable_name_stem_prev = obj.variable_name_stem
            self.n_variables_prev = obj.n_variables

        super().save(*args, **kwargs)

    def get_var_names(self):
        var_names = []
        for v in range(0, self.n_variables):
            var_name = self.variable_name_stem + '_' + str(v+1)
            var_names.append(var_name)
        return var_names

    def execute(self, sub):
        response = QuestionnaireResponse.objects.filter(
            submission=sub,
            variable=self.related_upload_question.variable
        ).first()

        if response is None:
            # TODO: raise/log error
            return

        upload_id = response.answer

        # Retrieve the uploaded data.
        raw_data = UploadedData.objects.get(upload_id=upload_id).data
        data = json.loads(raw_data)

        entries = []
        # Extract random entries.
        if len(data) < self.n_variables:
            for i in range(0, self.n_variables):
                if i >= len(data):
                    entries.append(None)
                else:
                    entries.append(i)
        else:
            entries += random.sample(range(0, len(data)), self.n_variables)

        for v in range(0, self.n_variables):
            var_name = self.variable_name_stem + '_' + str(v+1)
            var = Variable.objects.get(
                name=var_name,
                questionnaire=self.questionnaire
            )
            e = entries.pop()
            if e is None:
                answer = self.questionnaire.missing_invalid
            else:
                data_entry = data[e]
                if self.field_to_extract in data_entry:
                    answer = data_entry[self.field_to_extract]
                else:
                    answer = self.questionnaire.missing_invalid

            QuestionnaireResponse.objects.create(
                submission=sub,
                variable=var,
                answer=answer
            )

        return


class EmailTrigger(Trigger):
    """
    Sends out an e-mail (with or without delay) when executed.

    Attributes:
        from_email (str): The e-mail address to use as the sender of the e-mail.
        to_email (str): The receiving e-mail address.
        subject (str): The subject of the e-mail.
        message (str): The message body of the e-mail.
        execution_time (str): Can either be 'immediately' or 'delayed'.
            If set to 'immediately', the e-mail will be send on execution of the
            trigger.
            If set to 'delayed', the e-mail will be send x minutes after the
            execution of the trigger (as defined in execution_delay).
        execution_delay (int): The delay time in minutes between executing the
            trigger and sending the e-mail. Is only effective if execution_time
            is set to 'delayed'.
    """
    DEFAULT_TRIGGER_TYPE = Trigger.TYPE_EMAIL

    # Sender configuration.
    from_email = models.CharField(
        max_length=254,
        default='contact@digital-meal.ch',
        verbose_name='Sender'
    )

    # Receiver configuration.
    to_email = models.CharField(
        max_length=254,
        verbose_name='Receiver',
        null=True,
        blank=True
    )

    # Content configuration.
    subject = models.CharField(max_length=150)
    message = models.TextField()

    # Execution point configuration.
    EXECUTE_IMMEDIATELY = 'immediately'
    EXECUTE_DELAYED = 'delayed'
    EXECUTION_TIMES = [
        (EXECUTE_IMMEDIATELY, 'immediately'),
        (EXECUTE_DELAYED, 'delayed')
    ]
    # TODO: Rename to execution_type to increase code readability
    execution_time = models.CharField(
        max_length=20,
        choices=EXECUTION_TIMES,
        default=EXECUTE_IMMEDIATELY
    )

    execution_delay = models.IntegerField(
        default=0,
        help_text='Execution delay time in minutes.'
    )

    def execute(self, sub):
        # check execution time
        if self.execution_time == self.EXECUTE_IMMEDIATELY:
            self.send_mail(sub)
        elif self.execution_time == self.EXECUTE_DELAYED:
            # register trigger task
            ex_time = (
                datetime.now(tz=SQ_TIMEZONE) +
                timedelta(minutes=self.execution_delay)
            )
            ex_type = self.DEFAULT_TRIGGER_TYPE
            ex_info = {
                'trigger_pk': self.pk,
                'sub_pk': sub.pk,
            }

            task = TriggerTask(
                execution_time=ex_time,
                execution_type=ex_type,
                execution_info=ex_info
            )
            task.save()
        else:
            # TODO: Catch error.
            pass

        return

    def send_mail(self, sub):
        # Account for possible variable references in the from and to address.
        frm = fill_variable_placeholder(self.from_email, sub)
        to = fill_variable_placeholder(self.to_email, sub)

        # Check if sender and reveiver e-mail addresses are valid.
        try:
            validate_email(frm)
            validate_email(to)
        except:
            return

        # Account for possible variable references in the subject and message.
        subject = fill_variable_placeholder(self.subject, sub)
        message = fill_variable_placeholder(self.message, sub)

        # Send e-mail.
        send_mail(subject, message, frm, [to])
        return


class CleanUploadDataTrigger(Trigger):
    """On execution, deletes all UploadData and UploadDataTemp objects
    belonging to the given submission that are listed in UploadDataTemp.
    """
    DEFAULT_TRIGGER_TYPE = Trigger.TYPE_CLEAN_UL_DATA

    def execute(self, sub):
        questionnaire = self.questionnaire

        # Get all filefeedback questions.
        ff_questions = questionnaire.get_questions().filter(
            question_type=FileFeedback.DEFAULT_QUESTION_TYPE)

        for question in ff_questions:
            upload_id = question.get_upload_id(sub)
            ul_data_temp = get_or_none(UploadedDataTemp, upload_id=upload_id)

            # If upload_id is registered in UploadDataTemp.
            if ul_data_temp is not None:
                # Delete UploadData with upload_id.
                ul_data = get_or_none(UploadedData, upload_id=upload_id)
                if ul_data is not None:
                    ul_data.delete()

                # TODO: Check the Code fragment below -> What is this?
                # delete UploadDataTemp with upload_id
                # ul_data_temp

        return


class TriggerTask(models.Model):
    """
    Is used to register a trigger for a delayed execution. All tasks registered
    here are checked in certain intervals through a CRON job on the server
    and are handled if the execution_time is in the past.
    Currently is only used to send e-mails issued by e-mail triggers with a
    delayed execution time.

    Attributes:
        execution_time (datetime): The date time, after which the trigger task
            should be handled.
        execution_type (str): The trigger type. Currently, only supports e-mail
            triggers. Other registered trigger types will be ignored.
        execution_info (json): The relevant trigger information in json format
            that is needed to execute the trigger task.
    """
    execution_time = models.DateTimeField()
    execution_type = models.CharField(
        max_length=50,
    )
    execution_info = JSONField(null=True, blank=True)
