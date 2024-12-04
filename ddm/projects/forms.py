from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_ckeditor_5.widgets import CKEditor5Widget

from ddm.projects.models import DonationProject

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
            'active',
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

    def clean(self):
        cleaned_data = super().clean()
        url_parameter_enabled = cleaned_data.get('url_parameter_enabled', False)
        expected_url_parameters = cleaned_data.get('expected_url_parameters', '')

        if url_parameter_enabled and not expected_url_parameters:
            self.add_error('expected_url_parameters',
                           'URL parameter is enabled but no parameter is defined to be extracted.')

        redirect_enabled = cleaned_data.get('redirect_enabled', False)
        redirect_target = cleaned_data.get('redirect_target', '')
        if redirect_enabled and not redirect_target:
            self.add_error('redirect_target',
                           'Redirect is enabled but no redirect target is defined.')

        return cleaned_data


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

    def clean(self):
        cleaned_data = super().clean()

        consent_enabled = cleaned_data.get('briefing_consent_enabled', False)
        consent_label_yes = cleaned_data.get('briefing_consent_label_yes', '')
        consent_label_no = cleaned_data.get('briefing_consent_label_no', '')
        consent_label_error_msg = 'When briefing consent is enabled, a consent label must be provided.'

        if consent_enabled and not consent_label_yes:
            self.add_error('briefing_consent_label_yes', consent_label_error_msg)

        if consent_enabled and not consent_label_no:
            self.add_error('briefing_consent_label_no', consent_label_error_msg)
        return cleaned_data

class DebriefingEditForm(forms.ModelForm):
    class Meta:
        model = DonationProject
        fields = ['debriefing_text']
        widgets = {
            'debriefing_text': CKEditor5Widget(config_name='ddm_ckeditor_temp_func'),
        }
