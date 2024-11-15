from django.utils import timezone

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
