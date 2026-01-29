from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, TextInput, Textarea

from django_ckeditor_5.widgets import CKEditor5Widget

from ddm.datadonation.models import DonationBlueprint, ProcessingRule, FileUploader, DonationInstruction


class BlueprintEditForm(forms.ModelForm):

    class Meta:
        model = DonationBlueprint
        fields = [
            'name',
            'description',
            'display_position',
            'regex_path',
            'exp_file_format',
            'csv_delimiter',
            'file_uploader',
            'json_extraction_root',
            'expected_fields',
            'expected_fields_regex_matching'
        ]
        widgets = {
            'expected_fields': forms.Textarea(attrs={'rows': 1}),
            'regex_path': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
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


class InstructionsForm(forms.ModelForm):
    class Meta:
        model = DonationInstruction
        fields = ['text', 'index']
        widgets = {
            'text': CKEditor5Widget(config_name='ddm_ckeditor'),
        }


class ProcessingRuleForm(forms.ModelForm):

    class Meta:
        model = ProcessingRule
        fields = [
            'execution_order',
            'name',
            'field',
            'regex_field',
            'comparison_operator',
            'comparison_value',
            'replacement_value'
        ]
        widgets = {
            'field': TextInput(),
            'comparison_value': Textarea(attrs={'cols': 60, 'rows': 1}),
            'replacement_value': Textarea(attrs={'cols': 60, 'rows': 1}),
        }


ProcessingRuleInlineFormset = inlineformset_factory(
    DonationBlueprint,
    ProcessingRule,
    form=ProcessingRuleForm,
    extra=0
)


class SecretInputForm(forms.Form):
    secret = forms.CharField(
        widget=forms.PasswordInput()
    )


class FileUploaderForm(forms.ModelForm):

    class Meta:
        model = FileUploader
        fields = [
            'name',
            'upload_type',
            'extract_nested_zips',
            'extraction_depth',
            'combined_consent',
            'index',
        ]
        labels = {
            'extract_nested_zips': 'Extract nested zip files',
            'extraction_depth': 'Extraction depth',
        }
        widgets = {
            'extraction_depth': forms.NumberInput(),
        }
        help_texts = {
            'combined_consent': (
                'If enabled, participants provide consent once for all data. '
                'Otherwise, they provide consent separately for each blueprint.'
            ),
            'index': (
                'Determines the position of this uploader in the donation interface '
                '(only relevant, if multiple uploaders are configured).'
            ),
            'extract_nested_zips': (
                'Whether to extract zip files found inside the uploaded zip and '
                'make their contents available to be handled by donation blueprints.'
            ),
            'extraction_depth': (
                'Maximum levels of nested zip files to extract '
                '(0 = only extract the top-level zip).'
            ),
        }
