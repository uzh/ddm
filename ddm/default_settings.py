# Default django-CKEditor configuration.
ddm_ckeditor = {
    'toolbar_custom': [
        {'name': 'basicstyles',
         'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
        {'name': 'paragraph',
         'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
                   'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'Blockquote', 'CreateDiv', '-']},
        {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
        {'name': 'insert',
         'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'SpecialChar']},
        {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
        {'name': 'colors', 'items': ['TextColor', 'BGColor']},
        {'name': 'tools', 'items': ['Maximize', 'ShowBlocks', 'Source']}
    ],
    'toolbar': 'custom',
    'allowedContent': True,
    'removePlugins': 'exportpdf',
    'entities': False,
    'extraPlugins': 'uploadimage',
}
