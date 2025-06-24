import json
import os

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.staticfiles import finders
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from ddm.projects.forms import (
    ProjectCreateForm, ProjectEditForm, BriefingEditForm, DebriefingEditForm,
    ProjectEditCustomUploaderTranslationsForm
)
from ddm.projects.models import DonationProject, ResearchProfile
from ddm.auth.views import DDMAuthMixin


class ProjectList(DDMAuthMixin, ListView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    template_name = 'ddm_projects/list.html'

    def get_queryset(self):
        return DonationProject.objects.filter(owner__user=self.request.user)


class ProjectCreate(SuccessMessageMixin, DDMAuthMixin, CreateView):
    """ View to create a new donation project. """
    model = DonationProject
    template_name = 'ddm_projects/create.html'
    form_class = ProjectCreateForm
    success_message = 'Project was created successfully.'

    def get_initial(self):
        self.initial = super().get_initial()
        self.initial.update({'owner': ResearchProfile.objects.get(user=self.request.user)})
        return self.initial

    def form_valid(self, form):
        form.instance.owner = ResearchProfile.objects.get(user=self.request.user)
        return super().form_valid(form)


class ProjectDetail(DDMAuthMixin, DetailView):
    """ View to display landing page for project. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/detail.html'


class ProjectEdit(SuccessMessageMixin, DDMAuthMixin, UpdateView):
    """ View to edit the details of an existing donation project. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/edit.html'
    form_class = ProjectEditForm
    success_message = 'Project details successfully updated.'


class ProjectEditCustomUploaderTranslations(
    SuccessMessageMixin,
    DDMAuthMixin,
    UpdateView
):
    """ View to add/edit custom uploader translations.  """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/edit_custom_uploader_translations.html'
    form_class = ProjectEditCustomUploaderTranslationsForm

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


class ProjectDelete(SuccessMessageMixin, DDMAuthMixin, DeleteView):
    """ View to display a list of existing donation projects. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/delete.html'
    success_url = reverse_lazy('ddm_projects:list')
    success_message = 'Project "%s" was deleted.'

    def get_success_message(self, cleaned_data):
        return self.success_message % self.object.name


class BriefingEdit(SuccessMessageMixin, DDMAuthMixin, UpdateView):
    """ View to edit the briefing page. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/edit-briefing.html'
    form_class = BriefingEditForm
    success_message = 'Briefing page successfully updated.'


class DebriefingEdit(SuccessMessageMixin, DDMAuthMixin, UpdateView):
    """ View to edit the debriefing page. """
    model = DonationProject
    slug_url_kwarg = 'project_url_id'
    slug_field = 'url_id'
    template_name = 'ddm_projects/edit-debriefing.html'
    form_class = DebriefingEditForm
    success_message = 'Debriefing page successfully updated.'
