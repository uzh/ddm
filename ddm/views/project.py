from django.views.generic.detail import DetailView

from ddm.models import DonationProject


class ProjectEntry(DetailView):
    model = DonationProject
    context_object_name = 'project'
    template_name = 'ddm/project/landing_page.html'
