from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView

from ddm.auth.views import DDMAuthMixin
from ddm.projects.models import DonationProject


class ProjectLogsView(SuccessMessageMixin, DDMAuthMixin, TemplateView):
    """ View that lists all exceptions related to a project. """
    template_name = 'ddm_logging/overview.html'

    def get_project(self):
        project_url_id = self.kwargs.get('project_url_id')
        return DonationProject.objects.filter(url_id=project_url_id).first()

    def get_event_logs(self):
        project = self.get_project()
        return project.eventlogentry_set.all()

    def get_exception_logs(self):
        project = self.get_project()
        return project.exceptionlogentry_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'project': self.get_project(),
            'events': self.get_event_logs(),
            'exceptions': self.get_exception_logs()
        })
        return context
