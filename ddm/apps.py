from django.apps import AppConfig


class SurquestConfig(AppConfig):
    name = 'surquest'

    def ready(self):
        import ddm.signals
