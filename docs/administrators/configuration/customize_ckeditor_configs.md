## Override the Configurations

Each CKEditor configuration defines what researchers can do in the editor, for example which toolbar
buttons and formatting options are available. If the defaults don't fit your needs, such as
when you want to remove the option to embed media or add a table tool, you can override them.

To do so, define the configuration in `CKEDITOR_5_CONFIGS` in `settings.py`. Your
configuration replaces DDM's default for that editor entirely; any editor you don't define
keeps its default.

The simplest way is to copy DDM's default from
[`ddm/core/ckeditor_config.py`](https://github.com/uzh/ddm/blob/develop/ddm/core/ckeditor_config.py)
and change only what you need:

```python
# settings.py

CKEDITOR_5_CONFIGS = {
    'ddm_ckeditor': {
        # Copy of DDM's default, with your changes.
    },
}
```

!!! warning

    If you override `ddm_ckeditor_temp_func`, keep support for the `<template-func>`
    element. Otherwise, researchers can't add dynamic content to their questions.

For available options, see the
[django-ckeditor-5 documentation](https://github.com/hvlads/django-ckeditor-5) and the
[CKEditor 5 documentation](https://ckeditor.com/docs/ckeditor5/latest/).
