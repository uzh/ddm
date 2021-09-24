from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ddm.models import (
    # Question Types
    Question, OpenQuestion, SingleChoiceQuestion, FileFeedback,
    FileUploadQuestion, MultiChoiceQuestion, TransitionQuestion, ListQuestion,
    MatrixQuestion, DifferentialQuestion,

    # Trigger Types
    Trigger, TokenGenerator, VariablesFromData,

    # Variables
    Variable, ExternalVariable,

    # Filter
    FilterSequence,

    # Other
    FileUploadItem, QuestionItem
)


@receiver(post_save, sender=OpenQuestion)
@receiver(post_save, sender=SingleChoiceQuestion)
@receiver(post_save, sender=FileUploadQuestion)
@receiver(post_save, sender=FileFeedback)
@receiver(post_save, sender=FileUploadItem)
@receiver(post_save, sender=QuestionItem)
@receiver(post_save, sender=ExternalVariable)
@receiver(post_save, sender=TokenGenerator)
def post_save_update_variable(sender, instance, created, **kwargs):
    """Updates Variables associated with the respective object.
    """

    i = instance

    if isinstance(i, Question):
        questionnaire = i.page.questionnaire
        rel_type = 'q'
    elif isinstance(i, QuestionItem):
        questionnaire = i.question.page.questionnaire
        rel_type = 'qi'
    elif isinstance(i, Trigger):
        questionnaire = i.questionnaire
        rel_type = 't'
    elif isinstance(i, ExternalVariable):
        questionnaire = i.questionnaire
        rel_type = 'ev'
    elif isinstance(i, FileUploadItem):
        questionnaire = i.file_upload_question.page.questionnaire
        rel_type = 'fu'

    if i.variable is None:
        var = Variable.objects.create(
            name=i.variable_name,
            questionnaire=questionnaire,
            related_type=rel_type
        )
        i.variable = var
        i.save()
    else:
        var = i.variable
        if i.variable_name != var.name:
            var.name = i.variable_name
            var.related_type = rel_type
            var.save()
    return


@receiver(post_delete, sender=QuestionItem)
def post_delete_variable(sender, instance, **kwargs):
    """Deletes the Variable Object related to the deleted object.
    """

    instance.variable.delete()
    return


@receiver(post_save, sender=VariablesFromData)
def post_save_update_vfd_variable(sender, instance, created, **kwargs):
    """Updates variable names associated with a 'Variables from Data' Trigger.
    """

    i = instance

    # Check if trigger has just been freshly created.
    if i.variable_name_stem_prev is None:
        # Create variables.
        for v in range(1, i.n_variables + 1):
            # Construct the variable name.
            var_name = i.variable_name_stem + '_' + str(v)
            Variable.objects.create(
                name=var_name,
                questionnaire=i.questionnaire,
                related_type='t'
            )
    else:
        # Check if the variable name stem has been altered.
        if i.variable_name_stem != i.variable_name_stem_prev:
            # Change names of the related variables.
            for v in range(1, i.n_variables_prev + 1):
                old_var_name = i.variable_name_stem_prev + '_' + str(v)
                new_var_name = i.variable_name_stem + '_' + str(v)

                var = Variable.objects.get(
                    name=old_var_name,
                    questionnaire=i.questionnaire
                )
                var.name = new_var_name
                var.save()

        # Check if the number of variables has been altered.
        if i.n_variables_prev < i.n_variables:
            # Create new variables.
            for v in range(i.n_variables_prev + 1, i.n_variables + 1):
                var_name = i.variable_name_stem + '_' + str(v)
                Variable.objects.create(
                    name=var_name,
                    questionnaire=i.questionnaire,
                    related_type='t'
                )

        elif i.n_variables_prev > i.n_variables:
            # Delete variables.
            for v in range(i.n_variables + 1, i.n_variables_prev + 1):
                var_name = i.variable_name_stem + '_' + str(v)
                Variable.objects.get(
                    name=var_name,
                    questionnaire=i.questionnaire,
                ).delete()
    return


@receiver(post_save, sender=OpenQuestion)
@receiver(post_save, sender=SingleChoiceQuestion)
@receiver(post_save, sender=MultiChoiceQuestion)
@receiver(post_save, sender=TransitionQuestion)
@receiver(post_save, sender=ListQuestion)
@receiver(post_save, sender=DifferentialQuestion)
@receiver(post_save, sender=MatrixQuestion)
@receiver(post_save, sender=FileFeedback)
@receiver(post_save, sender=FileUploadQuestion)
@receiver(post_save, sender=QuestionItem)
def post_create_filter_sequence(sender, instance, created, **kwargs):
    """Automatically creates a FilterSequence and associates it with the sender
    instance if no FilterSequence has yet been created.
    """

    # Check if the sender is a Question or QuestionItem instance.
    if isinstance(instance, Question):
        q = instance
        qi = None
    elif isinstance(instance, QuestionItem):
        q = None
        qi = instance

    f_seqs = FilterSequence.objects.filter(question=q, question_item=qi)
    if len(f_seqs) == 0:
        f_seq = FilterSequence(question=q, question_item=qi)
        f_seq.save()
    return
