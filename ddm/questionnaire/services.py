import copy
from typing import Any

from django.db import transaction
from django.utils import timezone

from ddm.logging.utils import log_server_exception
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.questionnaire.models import (
    FilterCondition,
    QuestionBase,
    QuestionItem,
    QuestionnaireResponse,
)


def get_question_item_response_key_list(project: DonationProject) -> list:
    """
    Returns a combined list of response keys for the questions and items in a project.

    The keys are formatted as strings with a prefix indicating the type:
    - "question-<id>" for each question in the project
    - "item-<id>" for each item associated with questions in the project

    Args:
        project (DonationProject): The project for which to retrieve response keys.

    Returns:
        list: A list of strings representing question and item response keys.
    """
    response_keys = []
    questions = QuestionBase.objects.filter(project=project)
    for q in questions:
        response_keys += q.get_response_keys()
    return response_keys


def response_is_valid(response: Any, valid_responses: list) -> bool:  # noqa: ANN401
    """
    Validate a single response against a list of valid responses.

    Args:
        response (any): The response to validate.
        valid_responses (list): A list of valid responses.

    Returns:
        bool: True if the response is valid, False otherwise.
    """
    # Special case: any value that can be converted to string is valid.
    if "__any_string__" in valid_responses:
        try:
            str(response)
            return True  # noqa: TRY300
        except Exception:  # noqa: BLE001
            # TODO: Log exception
            return False

    for valid in valid_responses:
        # Check for exact match.
        if response == valid:
            return True

        # Check for string-int/float/bool equivalence.
        try:
            if str(response).lower() == str(valid).lower():
                return True
        except Exception:  # noqa: BLE001, S112
            # TODO: Log exception.
            continue

    return False


def validate_responses(responses: dict, project: DonationProject) -> None:
    """
    Validates the complete set of posted questionnaire responses.

    Validation is done as follows:
        1. Identify missing responses.
        2. Identify excess responses.
        3. Validate expected responses using the `response_is_valid()` function.

    Any identified validation issues are logged in the project logs.
    This function does not raise exceptions for invalid responses. Instead,
    invalid responses are logged and still included in the saved dataset.

    Args:
        responses (dict): A dictionary of submitted responses with keys prefixed
            by either 'question-' or 'item-' and corresponding responses as values.
        project (DonationProject): The project context used for error logging.

    Returns:
        None

    Logs:
        - Any missing responses.
        - Any unexpected responses.
        - If a validation error of an expected response occurs.
    """
    expected_keys = get_question_item_response_key_list(project)

    # Check for missing keys.
    missing_keys = set(expected_keys) - responses.keys()
    if missing_keys:
        msg = (
            "Questionnaire Post Exception: "
            f"Posted responses are missing the following keys: {missing_keys}"
        )
        log_server_exception(project, msg)

    # Check for excess keys.
    excess_keys = responses.keys() - set(expected_keys)
    if excess_keys:
        msg = (
            "Questionnaire Post Exception: "
            f"Posted responses contain the following excess keys: {excess_keys}"
        )
        log_server_exception(project, msg)

    # Validate responses.
    overlap_keys = set(expected_keys) & responses.keys()
    for key in overlap_keys:
        if key.startswith("question-"):
            question_id = key.removeprefix("question-")
            question = QuestionBase.objects.get(project=project, pk=question_id)
        elif key.startswith("item-"):
            item_id = key.removeprefix("item-")
            item = QuestionItem.objects.get(question__project=project, pk=item_id)
            question = item.question
        else:
            continue

        valid_responses = question.get_valid_responses()
        if not response_is_valid(responses[key], valid_responses):
            msg = (
                f"Questionnaire Post Exception: Invalid response for {key} - "
                f"{responses[key]} not in {valid_responses}"
            )
            log_server_exception(project, msg)


def save_questionnaire_response_to_db(
    responses: dict,
    project: DonationProject,
    participant: Participant,
    questionnaire_config: list | None = None,
    is_complete: bool = True,  # noqa: FBT002
) -> None:
    """
    Validates and saves questionnaire responses submitted by a participant.

    Takes the raw response data and optionally the associated
    questionnaire configuration, performs validation on responses for both
    question-level and item-level inputs, and stores the validated data
    in the database.

    A participant has at most one QuestionnaireResponse per project: calling
    this again for the same participant (e.g. an in-progress save on an
    earlier page, followed by the final submission) updates that same row
    rather than creating a duplicate.

    Args:
        responses (dict): A dictionary of raw responses keyed by either
            'question-<id>' or 'item-<id>' (e.g., 'question-12': 1,
            'item-23': 0). Key prefixes ("question-"/"item-") are needed to
            differentiate between question-level and item-level data.
        project (DonationProject): The project instance to which this questionnaire
            is related.
        participant (Participant): The participant who submitted the responses.
        questionnaire_config (list): The questionnaire configuration as submitted
            by the frontend, describing the structure of the questionnaire at
            submission time.
        is_complete (bool): Whether this is the participant's final submission
            (True) or an in-progress save while they're still working through
            the questionnaire (False).

    Raises:
        ValidationError: If any of the question or item responses fail validation.

    Returns:
        None
    """
    validate_responses(responses, project)

    QuestionnaireResponse.objects.update_or_create(
        project=project,
        participant=participant,
        defaults={
            "time_submitted": timezone.now(),
            "data": responses,
            "questionnaire_config": questionnaire_config,
            "is_complete": is_complete,
        },
    )


def reset_pk(instance) -> None:  # noqa: ANN001
    """
    Clear pk for `instance`, including inherited parent-link pks for
    multi-table-inherited (e.g. django-polymorphic) models.

    A plain `instance.pk = None` only clears the local pk field. For MTI
    subclasses, ancestor tables have their own separately-stored pk
    attribute (e.g. `id` inherited from a polymorphic base model) that
    must also be cleared, or Django will UPDATE the ancestor row instead
    of inserting a new one.
    """
    for parent in instance._meta.get_parent_list():  # noqa: SLF001
        setattr(instance, parent._meta.pk.attname, None)  # noqa: SLF001
    instance.pk = None


def variable_name_unique(name: str, project: DonationProject) -> bool:
    return not QuestionBase.objects.filter(variable_name=name, project=project).exists()


@transaction.atomic
def copy_question(question: QuestionBase) -> QuestionBase:
    new_q = copy.deepcopy(question)
    reset_pk(new_q)

    base_variable_name = f"{question.variable_name}_copy"
    new_variable_name = base_variable_name
    i = 0
    while not variable_name_unique(new_variable_name, question.project):
        i += 1
        new_variable_name = f"{base_variable_name}_{i}"
    new_q.variable_name = new_variable_name
    new_q.name = f"{question.name} (copy)"
    new_q.save(force_insert=True)

    # copy question item
    for item in question.questionitem_set.all():
        item_new = copy.deepcopy(item)
        item_new.pk = None
        item_new.question = new_q
        item_new.save(force_insert=True)

        # copy item filter conditions
        filter_conditions = FilterCondition.objects.filter(target_item=item)
        for fc in filter_conditions:
            new_fc = copy.deepcopy(fc)
            new_fc.pk = None
            new_fc.target_item = item_new
            new_fc.save(force_insert=True)

    # copy scale points
    for sp in question.scalepoint_set.all():
        sp_new = copy.deepcopy(sp)
        sp_new.pk = None
        sp_new.question = new_q
        sp_new.save(force_insert=True)

    # copy question filter conditions
    filter_conditions = FilterCondition.objects.filter(target_question=question)
    for fc in filter_conditions:
        new_fc = copy.deepcopy(fc)
        new_fc.pk = None
        new_fc.target_question = new_q
        new_fc.save(force_insert=True)

    return new_q
