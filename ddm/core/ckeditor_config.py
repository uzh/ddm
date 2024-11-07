from copy import deepcopy


ddm_ckeditor =  {
    'blockToolbar': [
        'paragraph', 'heading1', 'heading2', 'heading3',
        '|',
        'bulletedList', 'numberedList',
        '|',
        'blockQuote',
    ],
    'toolbar': [
        'heading', '|',
        'alignment', 'outdent', 'indent', '|',
        'bold', 'italic', 'underline', 'link', 'highlight', '|',
        {
            'label': 'Fonts',
            'icon': 'text',
            'items': ['fontSize', 'fontFamily', 'fontColor']
        }, '|',
        'bulletedList', 'numberedList', 'insertTable', 'blockQuote', 'code', 'removeFormat', '|',
        'insertImage', 'fileUpload', 'mediaEmbed', '|',
        'sourceEditing'
    ],
    'image': {
        'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                    'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
        'styles': [
            'full',
            'side',
            'alignLeft',
            'alignRight',
            'alignCenter',
        ]
    },
    'table': {
        'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
                            'tableProperties', 'tableCellProperties' ],
    },
    'heading' : {
        'options': [
            { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
            { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
            { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
            { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
        ]
    },
    'htmlSupport': {
            'allow': [
                {
                    'name': 'video',
                    'attributes': {
                        'height': True,
                        'width': True,
                        'controls': True,
                    },
                    'styles': True
                }
            ],
            'disallow': []
        },
    'wordCount': {
        'displayCharacters': False,
        'displayWords': False,
    }
}

ddm_ckeditor_temp_func = deepcopy(ddm_ckeditor)
ddm_ckeditor_temp_func['heading']['options'].append(
    {'model': 'template-func', 'view': 'template-func', 'title': 'Template Functionality', 'class': 'template-func'})
