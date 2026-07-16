import json
from itertools import chain
from typing import Any

from ddm.participation.models import Participant
from ddm.participation.utils import get_filter_config_id
from ddm.projects.models import DonationProject


def get_url_parameters(
    project: DonationProject, participant: Participant | None = None
) -> dict:
    """
    Get a dictionary containing the url parameters collected for a given
    DonationProject as keys (="variable names") and if a participant is
    provided, the values collected for this participant
    (else the values are None).
    The variable name is constructed by prefixing the url parameter with "_url_"
    (e.g., "_url_parametername").

    Args:
        project (DonationProject): The DonationProject for which the
            variables should be collected.
        participant (Participant): The participant for which to return the
            variables (optional).

    Returns:
        dict: A dictionary containing variable names as keys and optional
            a participants variable values as values.
    """
    variable_dict = {}
    url_parameters = project.get_expected_url_parameters()
    for parameter in url_parameters:
        value = participant.url_parameter.get(parameter, None) if participant else None
        variable_dict[f"_url_{parameter}"] = value

    return variable_dict


def get_participant_variables(participant: Participant | None = None) -> dict:
    """
    Get a dictionary containing participant variables collected for a given
    DonationProject as keys and if a participant is provided, the values
    collected for this participant (else the values are None).

    Args:
        participant (Participant): The participant for which to return the
            variables (optional).

    Returns:
        dict: A dictionary containing variable names as keys and optional
            a participants variable values as values.
    """
    participant_variables = {
        # TODO: '_user_agent',
        "_participant_id": None,
        "_start_time": None,
        "_end_time": None,
        "_completed": None,
        "_briefing_consent": None,
    }
    if participant:
        if participant.start_time:
            start_time = participant.start_time.replace(microsecond=0).isoformat()
        else:
            start_time = None

        if participant.end_time:
            end_time = participant.end_time.replace(microsecond=0).isoformat()
        else:
            end_time = None

        participant_variables = {
            # TODO: '_user_agent',
            "_participant_id": participant.external_id,
            "_start_time": start_time,
            "_end_time": end_time,
            "_completed": participant.completed,
            "_briefing_consent": participant.extra_data.get("briefing_consent", None),
        }
    return participant_variables


def get_donation_variables(participant: Participant | None = None) -> dict[str, Any]:
    """
    Get a dictionary containing participant variables collected for a given
    DonationProject as keys and if a participant is provided, the values
    collected for this participant (else the values are None).

    Args:
        participant (Participant): The participant for which to return the
            variables (optional).

    Returns:
        dict: A dictionary containing variable names as keys and optional
            a participants variable values as values.
    """
    donation_info = participant.get_donation_info() if participant else {}
    return {
        "_donation_n_success": donation_info.get("n_success"),
        "_donation_n_pending": donation_info.get("n_pending"),
        "_donation_n_failed": donation_info.get("n_failed"),
        "_donation_n_consent": donation_info.get("n_consent"),
        "_donation_n_no_consent": donation_info.get("n_no_consent"),
        "_donation_n_no_data_extracted": donation_info.get("n_no_data_extracted"),
    }


def get_questionnaire_variables(
    project: DonationProject,
    participant: Participant | None = None,
    include_general: bool = True,  # noqa: FBT002
) -> dict:
    """
    Returns a list of the variables collected through the questionnaire.

    Args:
        project (DonationProject): The DonationProject for which the variables
            should be collected.
        participant (Participant): The participant for which to return the
            variables (optional).
        include_general (bool): Whether to include general variables.

    Returns:
        dict: A dictionary containing variable names as keys and optional
            a participants variable values as values.
    """
    from ddm.questionnaire.constants import QuestionType  # noqa: PLC0415
    from ddm.questionnaire.models import (  # noqa: PLC0415
        OpenQuestion,
        QuestionItem,
        QuestionnaireResponse,
        SingleChoiceQuestion,
    )

    variables = {}
    response = None
    response_data = None

    if participant:
        response = QuestionnaireResponse.objects.filter(
            participant=participant, project=project
        ).first()
        if response:
            response_data = response.get_decrypted_data(
                secret=project.secret_key, salt=project.get_salt()
            )
            response_data = json.loads(response_data)
        else:
            response_data = None

    if include_general and participant:
        if response.time_submitted:
            time_submitted = response.time_submitted.replace(microsecond=0).isoformat()
        else:
            time_submitted = None
        variables["_quest_time_submitted"] = time_submitted
    else:
        variables["_quest_time_submitted"] = None

    # Question variables
    sc_questions = SingleChoiceQuestion.objects.filter(project=project)
    open_questions = OpenQuestion.objects.filter(
        project=project, multi_item_response=False
    )
    items = QuestionItem.objects.filter(question__project=project).exclude(
        question__question_type=QuestionType.SINGLE_CHOICE
    )
    for obj in list(chain(sc_questions, open_questions, items)):
        var_name = obj.variable_name
        if not response_data:
            variables[var_name] = None
        else:
            response_id = get_filter_config_id(obj)
            variables[var_name] = response_data.get(response_id, None)

    return variables


def get_project_variables(project: DonationProject) -> list:
    """
    Get a list of all variables collected for a given DonationProject.

    Args:
        project: The DonationProject for which the variables should be collected.

    Returns:
        list: A list of variable names.
    """
    variables = []

    # System Variables
    variables.extend(get_url_parameters(project).keys())

    # Participant Variables
    variables.extend(get_participant_variables().keys())

    # Donation Variables
    variables.extend(get_donation_variables().keys())

    # Questionnaire Variables
    variables.extend(get_questionnaire_variables(project).keys())

    return variables
