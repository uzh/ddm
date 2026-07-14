from ddm.logging.models import ExceptionLogEntry, ExceptionRaisers
from ddm.projects.models import DonationProject


def log_server_exception(project: DonationProject, message: str) -> None:
    ExceptionLogEntry.objects.create(
        project=project, raised_by=ExceptionRaisers.SERVER, message=message
    )
