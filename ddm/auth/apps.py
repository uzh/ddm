from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DDMAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'ddm.auth'
    label = 'ddm_auth'
    verbose_name = _('DDM Authentication')
