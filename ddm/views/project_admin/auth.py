from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import reverse, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import TemplateView

from ddm.forms import ResearchProfileConfirmationForm, DdmUserCreationForm
from ddm.models import ResearchProfile, DonationProject

import re

"""
Password requirements etc. are controlled through the basic settings of the Django application.
Must be set in DDL: https://docs.djangoproject.com/en/3.2/topics/auth/passwords/#password-validation
"""


def email_is_valid(email_string):
    if hasattr(settings, 'DDM_SETTINGS'):
        if 'EMAIL_PERMISSION_CHECK' in settings.DDM_SETTINGS:
            match = re.match(settings.DDM_SETTINGS['EMAIL_PERMISSION_CHECK'],
                             email_string)
            if not match:
                return False
    return True


def user_is_permitted(request):
    if request.user.is_superuser:
        return True
    elif request.user.is_authenticated and email_is_valid(request.user.email):
        return True
    else:
        return False


def user_is_owner(user, project_pk):
    donation_project = DonationProject.objects.get(pk=project_pk)
    if donation_project.owner.user == user:
        return True
    else:
        return False


class DdmAuthMixin:
    """
    Mixin for Class Based Views that handles redirects
    - unauthenticated users => login page
    - users without research profiles => registration page
    - users without authorization (e.g., due to e-mail restriction) => no permission page
    - users without owner-rights => 404
    """
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            # Check if user is authenticated.
            if not request.user.is_authenticated:
                return redirect('ddm-login')
            elif not user_is_permitted(request):
                return redirect('ddm-no-permission')
            elif not ResearchProfile.objects.filter(user=request.user).exists():
                return redirect('ddm-register')
            else:
                if request.path not in [reverse('project-list'), reverse('project-create')]:
                    if 'project_pk' in self.kwargs:
                        project_pk = self.kwargs['project_pk']
                    else:
                        project_pk = self.kwargs['pk']
                    if not user_is_owner(request.user, project_pk) and not request.user.is_superuser:
                        return HttpResponseNotFound()
        return super().dispatch(request, *args, **kwargs)


class DdmLoginView(auth_views.LoginView):
    template_name = 'ddm/project_admin/generic/page_with_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if ResearchProfile.objects.filter(user=self.request.user).exists():
                return reverse('project-list')
            else:
                return redirect('ddm-register')
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self):
        if not self.request.user.is_authenticated:
            return reverse('ddm-login')
        elif ResearchProfile.objects.filter(user=self.request.user).exists():
            return reverse('project-list')
        else:
            return reverse('ddm-register')


class DdmRegisterResearchProfileView(CreateView):
    model = ResearchProfile
    form_class = ResearchProfileConfirmationForm
    template_name = 'ddm/project_admin/generic/page_with_form.html'
    success_url = reverse_lazy('project-list')

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if not request.user.is_authenticated:
                return redirect('ddm-login')
            elif not user_is_permitted(request):
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


class DdmCreateUserView(SuccessMessageMixin, CreateView):
    model = User
    form_class = DdmUserCreationForm
    template_name = 'ddm/project_admin/generic/page_with_form.html'
    success_url = reverse_lazy('ddm-login')
    success_message = 'Your profile was created successfully!'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.user.is_authenticated:
                if ResearchProfile.objects.filter(user=request.user).exists():
                    return redirect('project-list')
                else:
                    return redirect('ddm-register')
        return super().dispatch(request, *args, **kwargs)


class DdmNoPermissionView(TemplateView):
    template_name = 'ddm/project_admin/auth/no_permission.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if not request.user.is_authenticated:
                return redirect('ddm-login')
            elif (user_is_permitted(request) and
                  ResearchProfile.objects.filter(user=request.user).exists()):
                return redirect('project-list')
        return super().dispatch(request, *args, **kwargs)


class DdmLogoutView(auth_views.LogoutView):
    template_name = 'ddm/project_admin/generic/page_with_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if not request.user.is_authenticated:
                return redirect('ddm-login')
        return super().dispatch(request, *args, **kwargs)
