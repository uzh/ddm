from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from ddm.datadonation.models import DataDonation
from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers
from ddm.logging.utils import log_server_exception
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from ddm.questionnaire.exceptions import QuestionValidationError
from ddm.questionnaire.models import QuestionBase, QuestionnaireResponse


def save_questionnaire_to_db(
        data: dict,
        project: DonationProject,
        participant: Participant) -> None:
    """
    Takes a dictionary object containing information on a participant's
    responses to a project's questions, validates the responses, and saves the
    responses to the database.

    The expected data dictionary is of the form:
    {
      "question_id as str": {
        "response": <response>,
        "question": <question text>,
        "items": [
          {
            "id": <item id as int>,
            "label": <item label>,
            "label_alt": <item alt label>,
            "index": <item index>},
            "value": <value>,
            "randomize": <randomize (boolean)>
          },
          { <next item> }, ...
        ]
      },
      "next question_id as str": { ... },
    }
    """
    for question_id in data:
        try:
            question = QuestionBase.objects.get(pk=int(question_id))
        except QuestionBase.DoesNotExist:
            msg = ('Questionnaire Post Exception:'
                   f'Question with id={question_id} does not exist.')
            log_server_exception(project, msg)
            continue
        except (ValueError, TypeError):
            msg = ('Questionnaire Post Exception: Received invalid '
                   f'question_id ({question_id}) in questionnaire '
                   f'post_data.')
            log_server_exception(project, msg)
            continue

        try:
            question.validate_response(data[question_id]['response'])
        except QuestionValidationError as e:
            # Log validation errors but keep invalid value in data and save to the database.
            for error in e.errors:
                log_server_exception(project, error)

    QuestionnaireResponse.objects.create(
        project=project,
        participant=participant,
        time_submitted=timezone.now(),
        data=data
    )
    return


def create_questionnaire_config(project, participant, view):
    """
    Returns a dictionary containing all information to render the
    questionnaire for a given participant that
    can be passed to the vue questionnaire application.
    """
    q_config = []
    questions = project.questionbase_set.all().order_by('page', 'index')
    for question in questions:
        # If question is not associated to a donation blueprint.
        if question.is_general():
            q_config.append(question.get_config(participant, view))
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
                q_config.append(question.get_config(participant, view))
    return q_config


def create_filter_config(project):
    """
    Returns a dictionary containing the filter condition configurations that
    can be passed to the vue questionnaire application.
    """
    f_config = {}
    questions = project.questionbase_set.all()

    for question in questions:
        question_key = question.get_filter_config_id(question)
        f_config[question_key] = question.get_filter_config()

        items = question.questionitem_set.all()
        for item in items:
            item_key = item.get_filter_config_id(item)
            f_config[item_key] = item.get_filter_config()

    return f_config
