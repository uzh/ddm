from django.apps import AppConfig


class DdmConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'ddm'
    verbose_name = 'Data Donation Module'

    def ready(self):
        from ddm import signals

        # Add default settings for DDM if they are not defined in main application's settings.py.
        from django.conf import settings
        from ddm import default_settings as defaults

        if not hasattr(settings, 'CKEDITOR_CONFIGS'):
            setattr(settings, 'CKEDITOR_CONFIGS', {})
        if 'ddm_ckeditor' not in settings.CKEDITOR_CONFIGS:
            settings.CKEDITOR_CONFIGS['ddm_ckeditor'] = defaults.ddm_ckeditor
