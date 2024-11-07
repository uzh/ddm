from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_ckeditor_5.widgets import CKEditor5Widget

from ddm.projects.models import DonationProject, ResearchProfile

User = get_user_model()


class ProjectCreateForm(forms.ModelForm):
    project_password = forms.CharField(
        min_length=10,
        max_length=150,
        required=False,
        widget=forms.PasswordInput()
    )
    project_password_confirm = forms.CharField(
        min_length=10,
        max_length=150,
        required=False,
        widget=forms.PasswordInput()
    )

    class Meta:
        model = DonationProject
        fields = [
            'name',
            'slug',
            'super_secret',
            'owner',
            'contact_information',
            'data_protection_statement'
        ]
        widgets = {
            'owner': forms.HiddenInput(),
        }

    field_order = [
        'name',
        'slug',
        'super_secret',
        'project_password',
        'project_password_confirm',
        'contact_information',
        'data_protection_statement'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            self.fields['owner'].initial = kwargs['initial']['owner']

    def clean(self):
        super_secret = self.data.get('super_secret', False)
        secret = self.data.get('project_password', None)
        secret_confirm = self.data.get('project_password_confirm', None)

        if super_secret and secret in ['', None]:
            raise ValidationError('Super secret project needs a project password.')

        if super_secret and (secret != secret_confirm):
            raise ValidationError('The two supplied project passwords do not match".')

        super().clean()

    def save(self, commit=True):
        project = super().save(commit=False)
        if project.super_secret:
            project.secret_key = self.data['project_password']
        project.save()
        return project


class ProjectEditForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = [
            'name',
            'slug',
            'contact_information',
            'data_protection_statement',
            'url_parameter_enabled',
            'expected_url_parameters',
            'redirect_enabled',
            'redirect_target',
            'img_header_left',
            'img_header_right'
        ]
        widgets = {
            'data_protection_statement': CKEditor5Widget(config_name='ddm_ckeditor'),
            'contact_information': CKEditor5Widget(config_name='ddm_ckeditor'),
        }


class BriefingEditForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = [
            'briefing_text',
            'briefing_consent_enabled',
            'briefing_consent_label_yes',
            'briefing_consent_label_no'
        ]
        widgets = {
            'briefing_text': CKEditor5Widget(config_name='ddm_ckeditor'),
        }


class DebriefingEditForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = ['debriefing_text']
        widgets = {
            'debriefing_text': CKEditor5Widget(config_name='ddm_ckeditor_temp_func'),
        }


class ResearchProfileConfirmationForm(forms.ModelForm):
    confirmed = forms.BooleanField()

    class Meta:
        model = ResearchProfile
        fields = ['user']
        widgets = {'user': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_user_id = kwargs['initial']['user']
        self.fields['user'].initial = self.expected_user_id
        self.fields['confirmed'].initial = True
        self.fields['confirmed'].widget = forms.HiddenInput()

    def is_valid(self):
        if super().is_valid():
            return self.cleaned_data['confirmed']
        else:
            return False

    def save(self):
        """
        Ensure that user.id is not changed manually (e.g., by altering the HTML).
        """
        if self.cleaned_data['user'].pk != self.expected_user_id:
            raise ValidationError('User is not set as expected.', code='not allowed')
        return super().save()
