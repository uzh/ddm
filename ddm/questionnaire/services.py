from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from ddm.datadonation.models import DataDonation
from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers
from ddm.logging.utils import log_server_exception
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.questionnaire.models import (
    QuestionBase, QuestionnaireResponse, QuestionItem, get_filter_config_id)


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


def response_is_valid(response: any, valid_responses: list) -> bool:
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
            return True
        except Exception:
            return False

    for valid in valid_responses:
        # Check for exact match.
        if response == valid:
            return True

        # Check for string-int/float/bool equivalence.
        try:
            if str(response).lower() == str(valid).lower():
                return True
        except Exception:
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
        msg = ('Questionnaire Post Exception: '
               f'Posted responses are missing the following keys: {missing_keys}')
        log_server_exception(project, msg)

    # Check for excess keys.
    excess_keys = responses.keys() - set(expected_keys)
    if excess_keys:
        msg = ('Questionnaire Post Exception: '
               f'Posted responses contain the following excess keys: {excess_keys}')
        log_server_exception(project, msg)

    # Validate responses.
    overlap_keys = set(expected_keys) & responses.keys()
    for key in overlap_keys:
        if key.startswith('question-'):
            question_id = key.lstrip('question-')
            question = QuestionBase.objects.get(project=project, pk=question_id)
        elif key.startswith('item-'):
            item_id = key.lstrip('item-')
            item = QuestionItem.objects.get(question__project=project, pk=item_id)
            question = item.question
        else:
            continue

        valid_responses = question.get_valid_responses()
        if not response_is_valid(responses[key], valid_responses):
            msg = (f'Questionnaire Post Exception: Invalid response for {key} - '
                   f'{responses[key]} not in {valid_responses}')
            log_server_exception(project, msg)


def save_questionnaire_response_to_db(
        responses: dict,
        project: DonationProject,
        participant: Participant,
        questionnaire_config: list = None) -> None:
    """
    Validates and saves questionnaire responses submitted by a participant.

    Takes the raw response data and optionally the associated
    questionnaire configuration, performs validation on responses for both
    question-level and item-level inputs, and stores the validated data
    in the database.

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

    Raises:
        ValidationError: If any of the question or item responses fail validation.

    Returns:
        None
    """
    validate_responses(responses, project)

    QuestionnaireResponse.objects.create(
        project=project,
        participant=participant,
        time_submitted=timezone.now(),
        data=responses,
        questionnaire_config=questionnaire_config
    )
    return


def create_questionnaire_config(project: DonationProject,
                                participant: Participant) -> list:
    """
    Returns a dictionary containing all information to render the
    questionnaire for a given participant that can be passed to the frontend
    questionnaire application.

    Args:
        project (DonationProject): The project instance to which this questionnaire
            is related.
        participant (Participant): The participant for which the questionnaire
            will be rendered.

    Returns:
        list: A list in which each entry relates to one question and contains
            all information needed to render the question.
    """
    q_config = []
    questions = project.questionbase_set.all().order_by('page', 'index')
    for question in questions:
        # If question is not associated to a donation blueprint.
        if question.is_general():
            q_config.append(question.get_config(participant))
        else:
            try:
                donation = DataDonation.objects.get(
                    blueprint=question.blueprint,
                    participant=participant
                )
            except ObjectDoesNotExist:
                msg = ('Questionnaire Rendering Exception: No donation '
                       f'found for participant {participant.pk} and '
                       f'blueprint {question.blueprint.pk}.')
                ExceptionLogEntry.objects.create(
                    project=project,
                    raised_by=ExceptionRaisers.SERVER,
                    message=msg
                )
                continue

            if donation.consent and donation.status == 'success':
                q_config.append(question.get_config(participant))
    return q_config


def create_filter_config(project: DonationProject) -> dict:
    """
    Returns a dictionary containing the filter condition configurations
    for the given project that can be passed to the frontend questionnaire
    application.

    Args:
        project (DonationProject): The project for which the filter configuration
            should be generated.

    Returns:
        dict: A dictionary containing the project's filter condition
            (key: question/item identifier ['question-<question.pk>'/'item-<item.pk>'];
            value: a list of filter conditions for the question/item).
    """
    f_config = {}
    questions = project.questionbase_set.all()

    for question in questions:
        question_key = get_filter_config_id(question)
        f_config[question_key] = question.get_filter_config()

        items = question.questionitem_set.all()
        for item in items:
            item_key = get_filter_config_id(item)
            f_config[item_key] = item.get_filter_config()

    return f_config
