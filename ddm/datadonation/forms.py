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


class BlueprintEditForm(forms.ModelForm):

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
        }
        help_texts = {
            'display_name': (
                'A name for this blueprint, displayed to participants (e.g., "Watch History").'
            ),
            'description': (
                'Describe what data this blueprint extracts '
                '(e.g., "The titles of videos you watched and when you watched them"). '
                'Displayed to participants.'
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
        labels = {
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
            'combined_consent': 'All-in-one consent enabled'
        }
        widgets = {
            'extraction_depth': forms.NumberInput(),
        }
        help_texts = {
            'display_name': (
                'A name for this Uploader, displayed to participants '
                '(e.g., "TikTok Data Donation").'
            ),
            'combined_consent': '',
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
