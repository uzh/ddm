from django.db import models
from django.urls import reverse
from polymorphic.models import PolymorphicModel


class Page(PolymorphicModel):
    questionnaire = models.ForeignKey(
        'Questionnaire',
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=255)
    index = models.PositiveIntegerField(default=1)
    show_back_button = models.BooleanField(default=False)

    PAGE_TYPE_QUESTION = 'questionpage'
    PAGE_TYPE_END = 'endpage'
    PAGE_TYPES = [
        (PAGE_TYPE_QUESTION, 'Question Page'),
        (PAGE_TYPE_END, 'End Page'),
    ]
    DEFAULT_PAGE_TYPE = PAGE_TYPE_QUESTION
    page_type = models.CharField(
        max_length=50,
        choices=PAGE_TYPES,
        default=DEFAULT_PAGE_TYPE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'questionnaire'],
                name='unique_name_per_questionnaire'
            ),
        ]
        ordering = ['index']

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        kwargs['page_type'] = self.DEFAULT_PAGE_TYPE
        super().__init__(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(self.page_type + '-update',
                       kwargs={'pk': self.pk, 'q': self.questionnaire.pk})

    def save(self, *args, **kwargs):
        existing_pages = self.questionnaire.page_set.all()
        existing_indices = list(existing_pages.values_list('index', flat=True))

        if not self.pk:
            # Set index to max + 1.
            if len(existing_indices) > 0:
                self.index = max(existing_indices) + 1
            else:
                self.index = 1

        super().save(*args, **kwargs)

    def execute_triggers(self, execution_point, submission):
        """Execute triggers related to the page.

        Retrieves all triggers related to a question that have the provided
        execution_point and executes these triggers on after another.

        Args:
            execution_point (str): Must be 'before' or 'after'. When 'before',
                all triggers with execution point before the page is loaded are
                executed. When 'after', all triggers with execution point after
                the page has been submitted are executed.
            submission (QuestionnaireSubmission): The current
                QuestionnaireSubmission instance.

        Returns:
            None
        """

        if execution_point not in ['before', 'after']:
            # TODO: raise error
            return
        else:
            triggers = self.trigger_set.filter(execution_point=execution_point)

            for trigger in triggers:
                trigger.execute(submission)

            return


class QuestionPage(Page):
    DEFAULT_PAGE_TYPE = Page.PAGE_TYPE_QUESTION


class EndPage(Page):
    DEFAULT_PAGE_TYPE = Page.PAGE_TYPE_END

    redirect = models.BooleanField(default=False)
    redirect_url = models.URLField(
        blank=True,
        null=True,
        help_text='Only required if "redirect" is selected.'
    )
