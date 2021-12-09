from django.core.management.base import BaseCommand

from datetime import datetime

from ddm.models import TriggerTask, EmailTrigger, QuestionnaireSubmission
from ddm.settings import SQ_TIMEZONE
from ddm.tools import get_or_none


class Command(BaseCommand):
    """
    TODO: Add description
    """
    def handle(self, *args, **options):
        # Get all the tasks for which the execution time is in the past.
        current_time = datetime.now(tz=SQ_TIMEZONE)
        tasks = TriggerTask.objects.filter(execution_time__lt=current_time)

        self.stdout.write(str(len(tasks)), ending='')

        for task in tasks:
            # Handle all e-mail triggers.
            if task.execution_type == 'emailtrigger':
                trigger_pk = task.execution_info['trigger_pk']
                trigger = get_or_none(EmailTrigger, pk=trigger_pk)

                if trigger is not None:
                    # Check if the associated questionnaire is still active.
                    if trigger.questionnaire.active:
                        # Get the related submission.
                        sub_pk = task.execution_info['sub_pk']
                        sub = get_or_none(QuestionnaireSubmission, pk=sub_pk)

                        if sub is not None:
                            # Execute the trigger.
                            trigger.send_mail(sub)

                # After the trigger has been executed, delete the task.
                task.delete()

        return
