from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView

from ddm.auth.views import DDMAuthMixin
from ddm.logging.models import ExceptionLogEntry
from ddm.projects.models import DonationProject


class EventLogsListView(SuccessMessageMixin, DDMAuthMixin, TemplateView):
    project = None
    template_name = 'ddm_logging/event_log_list.html'

    def get_project(self):
        if self.project is None:
            project_url_id = self.kwargs.get('project_url_id')
            project = DonationProject.objects.filter(url_id=project_url_id).first()
            self.project = project
        return self.project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'project': self.get_project(),
        })
        return context


class ExceptionLogsListView(SuccessMessageMixin, DDMAuthMixin, TemplateView):
    project = None
    template_name = 'ddm_logging/exception_log_list.html'

    def get_project(self):
        if self.project is None:
            project_url_id = self.kwargs.get('project_url_id')
            self.project = DonationProject.objects.filter(
                url_id=project_url_id
            ).first()
        return self.project

    def sort_select_options(self, options: list | set) -> list:
        l = list(options)
        l = [str(e) for e in l if e is not None]
        l.sort()
        return l

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        qs = ExceptionLogEntry.objects.filter(project=project)

        types = set(qs.values_list('exception_type', flat=True))
        raised_by = set(qs.values_list('raised_by', flat=True))
        blueprints = set(qs.values_list('blueprint__name', flat=True))

        context.update({
            'types_select': self.sort_select_options(types),
            'raised_by_select': self.sort_select_options(raised_by),
            'blueprints_select': self.sort_select_options(blueprints),
            'project': self.get_project(),
        })
        return context
