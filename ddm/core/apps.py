from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DDMCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'ddm.core'
    label = 'ddm_core'
    verbose_name = _('DDM Core')
