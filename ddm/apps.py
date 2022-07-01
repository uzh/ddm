from django.apps import AppConfig


class DdmConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'ddm'
    verbose_name = 'Data Donation Module'

    def ready(self):
        from ddm import signals
