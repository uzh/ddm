from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from ddm.models import ResearchProfile
from ddm.views.project_admin import auth


class DdmUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if not auth.email_is_valid(email):
            raise forms.ValidationError(
                'Only researchers with a valid UZH e-mail address can register.'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            ResearchProfile.objects.create(user=user)
        return user


class ResearchProfileConfirmationForm(forms.ModelForm):
    confirmed = forms.BooleanField()

    class Meta:
        model = ResearchProfile
        fields = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].initial = kwargs['initial']['user']
        self.fields['confirmed'].initial = True
        self.fields['confirmed'].widget = forms.HiddenInput()

    def is_valid(self):
        if super().is_valid():
            return self.cleaned_data['confirmed']
        else:
            return False
