from ddm.models.core import Participant


def get_participant_from_request(request, project):
    try:
        participant_id = request.session[f'project-{project.pk}']['participant_id']
    except KeyError:
        raise

    try:
        participant = Participant.objects.get(pk=participant_id)
        return participant
    except Participant.DoesNotExist:
        raise
