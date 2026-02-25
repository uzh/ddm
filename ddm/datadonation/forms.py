from django import forms
from django.forms import inlineformset_factory, TextInput, Textarea
from django.utils.safestring import mark_safe

from django_ckeditor_5.widgets import CKEditor5Widget

from ddm.datadonation.models import (
    BlueprintFilePath,
    DonationBlueprint,
    DonationInstruction,
    FileUploader,
    ProcessingRule,
)


class BlueprintForm(forms.ModelForm):

    class Meta:
        model = DonationBlueprint
        fields = [
            'name',
            'display_name',
            'description',
            'display_position',
            'exp_file_format',
            'csv_delimiter',
            'file_uploader',
            'json_extraction_root',
            'expected_fields',
            'expected_fields_regex_matching'
        ]
        widgets = {
            'expected_fields': forms.Textarea(attrs={'rows': 1}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'expected_fields_regex_matching': 'Expected fields use regex matching',
            'display_position': 'Display order',
        }
        help_texts = {
            'name': 'For internal use (e.g., "watch_history")',
            'display_name': (
                'Title of the Blueprint shown to participants '
                '(e.g., "Watch History").'
            ),
            'display_position': (
                'Controls display order in Blueprint list. Lower = first.'
            ),
            'description': (
                'Explains to participants what data is extracted '
                '(e.g., "Videos you watched and when")'
            ),
            'expected_fields': mark_safe(
                'Comma-separated, in double quotes: <code>"Field A", "Field B"</code>'
            ),
            'expected_fields_regex_matching': '',
            'csv_delimiter': mark_safe(
                'The character that separates values in the CSV '
                '(e.g., <code>,</code> <code>;</code> or <code>\\t</code> for tab). '
                'If left empty, the delimiter is inferred automatically.'
            ),
            'json_extraction_root': mark_safe(
                'Optional: The root of the data structure from which to extract data. '
                'Leave empty to extract from the top level. </b>'
                'To extract from a nested level, specify the path using dot '
                'notation (e.g., <code>friends.real_friends</code>).'
            )
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if name and self.project:
            qs = DonationBlueprint.objects.filter(name=name, project=self.project)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                msg = (
                    'A Blueprint with this name already exists '
                    'in this project. Please choose another one.'
                )
                self.add_error('name', msg)

        return cleaned_data


class InstructionsForm(forms.ModelForm):
    class Meta:
        model = DonationInstruction
        fields = ['index', 'text']
        widgets = {
            'text': CKEditor5Widget(config_name='ddm_ckeditor'),
        }

        labels = {
            'index': 'Page number',
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
        help_texts = {
            'replacement_value': 'The replacement for matched text.',
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
            'display_name',
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
            'combined_consent': 'All-in-one consent',
            'index': 'Display position'
        }
        widgets = {
            'extraction_depth': forms.NumberInput(),
        }
        help_texts = {
            'name': 'For internal use (e.g., "tiktok_uploader")',
            'display_name': (
                'Title of the Uploader shown to participants '
                '(e.g., "TikTok Data Donation")'
            ),
            'combined_consent': '',
            'index': (
                'Controls display order when multiple Uploaders exist. '
                'Lower = first.'
            ),
            'extract_nested_zips': (
                'When enabled, any zip files found inside the uploaded zip '
                'are automatically extracted up to the extraction depth '
                'so their contents can be processed by Blueprints.'
            ),
            'extraction_depth': (
                'Levels of nested zips to extract (0 = top-level only)'
            ),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if name and self.project:
            qs = FileUploader.objects.filter(name=name, project=self.project)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                msg = (
                    'A File Uploader with this name already exists '
                    'in this project. Please choose another one.'
                )
                self.add_error('name', msg)

        return cleaned_data


class BlueprintFilePathForm(forms.ModelForm):

    class Meta:
        model = BlueprintFilePath
        fields = [
            'path',
            'is_regex',
            'priority',
        ]
        widgets = {
            'path': Textarea(attrs={'cols': 60, 'rows': 1}),
        }
        labels = {
            'path': 'File path',
        }


BlueprintFilePathInlineFormset = inlineformset_factory(
    DonationBlueprint,
    BlueprintFilePath,
    form=BlueprintFilePathForm,
    extra=0
)
