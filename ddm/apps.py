from django.apps import AppConfig


class DdmConfig(AppConfig):
    name = 'ddm'
    verbose_name = 'Data Donation Module'

    def ready(self):
        import ddm.signals
