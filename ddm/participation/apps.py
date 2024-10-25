from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DDMParticipationConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'ddm.participation'
    label = 'ddm_participation'
    verbose_name = _('DDM Participation')
