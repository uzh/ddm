from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DDMLoggingConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'ddm.logging'
    label = 'ddm_logging'
    verbose_name = _('DDM Logging')
