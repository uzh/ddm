from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers


def log_server_exception(project, message):
    ExceptionLogEntry.objects.create(
        project=project,
        raised_by=ExceptionRaisers.SERVER,
        message=message
    )
    return
