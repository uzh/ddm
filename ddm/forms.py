from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, TextInput, Textarea

from ddm.models.core import ResearchProfile, DonationProject, DonationBlueprint, ProcessingRule, FileUploader

User = get_user_model()


class ProjectCreateForm(forms.ModelForm):
    secret = forms.CharField(min_length=10, max_length=150, required=False, widget=forms.PasswordInput())
    secret_confirm = forms.CharField(min_length=10, max_length=150, required=False, widget=forms.PasswordInput())

    class Meta:
        model = DonationProject
        fields = ['name', 'slug', 'super_secret', 'owner', 'contact_information', 'data_protection_statement']
        widgets = {'owner': forms.HiddenInput()}

    field_order = ['name', 'slug', 'super_secret', 'secret', 'secret_confirm', 'contact_information', 'data_protection_statement']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            self.fields['owner'].initial = kwargs['initial']['owner']

    def clean(self):
        super_secret = self.data.get('super_secret', False)
        secret = self.data.get('secret', None)
        secret_confirm = self.data.get('secret_confirm', None)

        if super_secret and secret in ['', None]:
            raise ValidationError('Super secret project needs a secret.')

        if super_secret and (secret != secret_confirm):
            raise ValidationError('Secret and Secret Confirm does not match".')

        super().clean()

    def save(self, commit=True):
        project = super().save(commit=False)
        if project.super_secret:
            project.secret_key = self.data['secret']
        project.save()
        return project


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


class BlueprintEditForm(forms.ModelForm):

    class Meta:
        model = DonationBlueprint
        fields = ['name', 'exp_file_format', 'csv_delimiter', 'file_uploader', 'regex_path',
                  'expected_fields']
        widgets = {
            'expected_fields': forms.Textarea(attrs={'rows': 3}),
            'regex_path': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        related_file_uploader = self.data.get('file_uploader', None)
        regex = self.data.get('regex_path', None)

        if related_file_uploader:
            file_uploader = FileUploader.objects.get(pk=related_file_uploader)
            if file_uploader.upload_type == FileUploader.UploadTypes.ZIP_FILE and regex in ['', None]:
                raise ValidationError(
                    'Donation Blueprints that belong to a ZIP file uploader must define '
                    'a regex pattern.'
                )
        super().clean()


class ProcessingRuleForm(forms.ModelForm):

    class Meta:
        model = ProcessingRule
        fields = ['execution_order', 'name', 'field', 'comparison_operator', 'comparison_value']
        widgets = {
            'field': TextInput(),
            'comparison_value': Textarea(attrs={'cols': 60, 'rows': 2})
        }


ProcessingRuleInlineFormset = inlineformset_factory(
    DonationBlueprint,
    ProcessingRule,
    form=ProcessingRuleForm,
    extra=0
)


class APITokenCreationForm(forms.Form):
    expiration_days = forms.IntegerField(
        initial=30,
        min_value=1,
        max_value=90,
        required=True
    )
    action = forms.CharField(
        max_length=20,
        initial='create',
        widget=forms.HiddenInput()
    )
