from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import reverse, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.views.generic.base import TemplateView

from ddm.auth.forms import TokenCreationForm
from ddm.auth.models import ProjectAccessToken
from ddm.auth.utils import user_is_permitted, user_is_owner
from ddm.forms import ResearchProfileConfirmationForm
from ddm.models.core import DonationProject, ResearchProfile


User = get_user_model()


class DdmAuthMixin:
    """
    Mixin for Class Based Views that handles redirects as follows:
    - unauthenticated users => login page.
    - users without research profiles => create research profile.
    - users without authorization (e.g., due to e-mail restriction) => no permission page.
    - users without owner-rights => 404.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if not request.user.is_authenticated:
                return redirect('ddm-login')
            elif not user_is_permitted(request.user):
                return redirect('ddm-no-permission')
            elif not ResearchProfile.objects.filter(user=request.user).exists():
                ResearchProfile.objects.create(user=request.user)
            else:
                if request.path not in [reverse('project-list'), reverse('project-create')]:
                    if 'project_pk' in self.kwargs:
                        project_pk = self.kwargs['project_pk']
                    else:
                        project_pk = self.kwargs['pk']
                    if not user_is_owner(request.user, project_pk) and not request.user.is_superuser:
                        raise Http404()
        return super().dispatch(request, *args, **kwargs)


class DdmRegisterResearchProfileView(CreateView):
    """
    View to create a research profile for a user.
    Implements the following redirects:
    * Logged-in users with a research profile are redirected to the project list.
    * Unauthenticated users are redirected to the login page.
    * Users without permission rights are redirected to the no-permission view.
    """
    model = ResearchProfile
    form_class = ResearchProfileConfirmationForm
    template_name = 'ddm/admin/auth/confirm_profile.html'
    success_url = reverse_lazy('project-list')

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if not request.user.is_authenticated:
                return redirect('ddm-login')
            elif not user_is_permitted(request.user):
                return redirect('ddm-no-permission')
            elif ResearchProfile.objects.filter(user=request.user).exists():
                return redirect('project-list')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        self.initial = super().get_initial()
        self.initial.update({'user': self.request.user.pk})
        return self.initial

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse('ddm-no-permission'))


class DdmNoPermissionView(TemplateView):
    """
    View to inform users that they do not have the needed permission rights.
    Implements the following redirects:
    * Unauthenticated users are redirected to the login page.
    * Logged-in users with permission and a research profile are redirected to the project list.
    """
    template_name = 'ddm/admin/auth/no_permission.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if not request.user.is_authenticated:
                return redirect('ddm-login')
            elif (user_is_permitted(request.user) and
                  ResearchProfile.objects.filter(user=request.user).exists()):
                return redirect('project-list')
        return super().dispatch(request, *args, **kwargs)


class ProjectTokenView(SuccessMessageMixin, DdmAuthMixin, FormView):
    """ View to see existing access token or generate a new one. """
    template_name = 'ddm/admin/project/token.html'
    form_class = TokenCreationForm

    def get_project(self):
        """ Returns current project. """
        project_id = self.kwargs.get('pk')
        return DonationProject.objects.filter(pk=project_id).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context.update({
            'project': project,
            'token': ProjectAccessToken.objects.filter(project=project).first()
        })
        return context

    def form_valid(self, form):
        """ If form is valid, either create new token or delete existing one. """
        project = self.get_project()
        if form.cleaned_data['action'] == 'create':
            project.create_token(expiration_days=form.cleaned_data['expiration_days'])

        if form.cleaned_data['action'] == 'delete':
            token = project.get_token()
            token.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project-token', kwargs={'pk': self.kwargs.get('pk')})
