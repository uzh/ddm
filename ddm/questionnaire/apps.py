from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DDMQuestionnaireConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'ddm.questionnaire'
    label = 'ddm_questionnaire'
    verbose_name = _('DDM Questionnaire')
