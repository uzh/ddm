from rest_framework import exceptions

from ddm.logging.models import EventLogEntry
from ddm.projects.models import DonationProject


class DDMAPIMixin:
    """
    Mixin containing ddm-specific methods to be combined with DRF-views.
    """
    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        Added EventLog entries.
        """
        if request.authenticators and not request.successful_authenticator:
            self.create_event_log(
                descr='Failed Attempt', msg='Authentication failed.')
            raise exceptions.NotAuthenticated()

        self.create_event_log(
            descr='Failed Attempt', msg='Permission Denied.')
        raise exceptions.PermissionDenied(detail=message, code=code)

    def get_project(self):
        """ Returns project instance. """
        return DonationProject.objects.filter(pk=self.kwargs['pk']).first()

    def create_event_log(self, descr, msg):
        """ Creates an event log entry related to the current project. """
        if self.request is not None:
            prefix = f'{self.request.get_full_path()} {self.request.method}: '
        else:
            prefix = ''
        return EventLogEntry.objects.create(
            project=self.get_project(), description=f'{prefix}{descr}', message=msg)
