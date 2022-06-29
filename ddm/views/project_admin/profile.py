from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView

from ddm.auth import user_is_permitted
from ddm.models import ResearchProfile

User = get_user_model()


class ProfileDetailView(SuccessMessageMixin, DetailView):
    template_name = 'ddm/project_admin/profile/profile_detail.html'
    model = User
    success_message = 'Profile updated.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('ddm-login')
        elif not user_is_permitted(request.user):
            return redirect('ddm-no-permission')
        elif not ResearchProfile.objects.filter(user=request.user).exists():
            return redirect('ddm-register')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = ResearchProfile.objects.filter(user=self.object).first()
        return context


class ProfileChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'ddm/project_admin/generic/page_with_form.html'
    success_url = reverse_lazy('ddm-pw-changed')
    success_message = 'Password changed.'


class ProfilePasswordChangedView(PasswordChangeDoneView):
    template_name = 'ddm/project_admin/profile/password_changed.html'
