import json
import os

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.staticfiles import finders
from django.urls import reverse_lazy, reverse
from django.utils.text import Truncator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.core.view_mixins import DDMContextMixin
from ddm.projects import forms
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.auth.views import DDMAuthMixin


class BaseProjectMixin(SuccessMessageMixin, DDMContextMixin, DDMAuthMixin):

    def get_breadcrumbs(self):
        return [('Projects', reverse_lazy('ddm_projects:list'))]

    def _project_crumb(self, linked=True):
        name = Truncator(self.object.name).chars(15)
        url = (
            reverse(
                'ddm_projects:detail',
                kwargs={'project_url_id': self.object.url_id}
            ) if linked else None
        )
        return (f'{name}', url)


class ProjectList(BaseProjectMixin, ListView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    template_name = 'ddm_projects/project_list.html'

    def get_breadcrumbs(self):
        return [('Projects', None)]

    def get_queryset(self):
        return DonationProject.objects.filter(owner__user=self.request.user)


class ProjectCreate(BaseProjectMixin, CreateView):
    """ View to create a new donation project. """
    model = DonationProject
    template_name = 'ddm_projects/project_create.html'
    form_class = forms.ProjectCreateForm
    success_message = 'Project was created successfully.'

    submit_label = 'Create Project'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append(('Create New Project', None))
        return crumbs

    def get_initial(self):
        self.initial = super().get_initial()
        self.initial.update({'owner': ResearchProfile.objects.get(user=self.request.user)})
        return self.initial

    def form_valid(self, form):
        form.instance.owner = ResearchProfile.objects.get(user=self.request.user)
        return super().form_valid(form)


class ProjectDetail(BaseProjectMixin, DetailView):
    """ View to display landing page for project. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/project_detail/base.html'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append(self._project_crumb(linked=False))
        return crumbs


class ProjectEditBase(BaseProjectMixin, UpdateView):
    """ View to edit the details of an existing donation project. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = None
    form_class = None
    success_message = 'Project details successfully updated.'

    submit_label = 'Update Project'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(('Details', None))
        return crumbs


class ProjectEditPublicInformation(ProjectEditBase):
    template_name = 'ddm_projects/project_edit/public_information.html'
    form_class = forms.EditPublicInformationForm

    def get_breadcrumbs(self):
        crumbs = [('Projects', reverse_lazy('ddm_projects:list'))]
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(('Public Information', None))
        return crumbs


class ProjectEditUrlParameter(ProjectEditBase):
    template_name = 'ddm_projects/project_edit/url_parameter_extraction.html'
    form_class = forms.EditUrlParameterExtractionForm

    def get_breadcrumbs(self):
        crumbs = [('Projects', reverse_lazy('ddm_projects:list'))]
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(('URL Parameter Extraction', None))
        return crumbs


class ProjectEditRedirectConfiguration(ProjectEditBase):
    template_name = 'ddm_projects/project_edit/redirect.html'
    form_class = forms.EditRedirectConfigurationForm

    def get_breadcrumbs(self):
        crumbs = [('Projects', reverse_lazy('ddm_projects:list'))]
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(('Redirect Configuration', None))
        return crumbs


class ProjectEditBranding(ProjectEditBase):
    template_name = 'ddm_projects/project_edit/branding.html'
    form_class = forms.EditBrandingForm

    def get_breadcrumbs(self):
        crumbs = [('Projects', reverse_lazy('ddm_projects:list'))]
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(('Branding', None))
        return crumbs


class ProjectEditCustomUploaderTranslations(BaseProjectMixin, UpdateView):
    """ View to add/edit custom uploader translations.  """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/uploader_translations_edit.html'
    form_class = forms.ProjectEditCustomUploaderTranslationsForm

    submit_label = 'Update Translations'

    def get_context_data(self, **kwargs):
        """
        Add locale files used by DDMUploader as reference to template
        context.
        """
        context = super().get_context_data(**kwargs)
        locales = {}
        locales_folder = finders.find('ddm_core/frontend/uploader/locale')

        if locales_folder and os.path.isdir(locales_folder):
            for filename in os.listdir(locales_folder):
                if filename.endswith('.json'):
                    locale_name = filename.split('.')[0]
                    file_path = os.path.join(locales_folder, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            locale_data = json.load(f)
                            locales[locale_name] = locale_data
                    except (json.JSONDecodeError, IOError):
                        pass

        context['locales'] = json.dumps(locales, indent=4, ensure_ascii=False)
        return context

    def get_success_message(self, cleaned_data):
        return (f'Custom translations for project "{self.object.name}" '
                f'successfully updated.')

    def get_success_url(self):
        return reverse(
            'ddm_projects:edit_translations',
            kwargs={'project_url_id': self.object.url_id}
        )

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(
            ('Data Donation',
             reverse(
                 'ddm_datadonation:overview',
                 kwargs={'project_url_id': self.object.url_id})
             )
        )
        crumbs.append(('Uploader Translations', None))
        return crumbs

class ProjectDelete(BaseProjectMixin, DeleteView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/project_delete.html'
    success_url = reverse_lazy('ddm_projects:list')
    success_message = 'Project "%s" was deleted.'

    submit_label = 'Delete Project'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(('Delete', None))
        return crumbs

    def get_success_message(self, cleaned_data):
        return self.success_message % self.object.name


class BriefingEdit(BaseProjectMixin, UpdateView):
    """ View to edit the briefing page. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/briefing_edit.html'
    form_class = forms.BriefingEditForm
    success_message = 'Briefing page successfully updated.'

    submit_label = 'Update Briefing'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(('Briefing Page', None))
        return crumbs


class DebriefingEdit(BaseProjectMixin, UpdateView):
    """ View to edit the debriefing page. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/debriefing_edit.html'
    form_class = forms.DebriefingEditForm
    success_message = 'Debriefing page successfully updated.'

    submit_label = 'Update Debriefing'

    def get_breadcrumbs(self):
        crumbs = super().get_breadcrumbs()
        crumbs.append(self._project_crumb(linked=True))
        crumbs.append(('Debriefing Page', None))
        return crumbs
