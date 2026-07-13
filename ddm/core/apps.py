from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DDMCoreConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ddm.core"
    label = "ddm_core"
    verbose_name = _("DDM Core")

    def ready(self) -> None:

        # Add default settings for DDM if they are not defined
        # in main application's settings.py.
        from django.conf import settings  # noqa: PLC0415

        from ddm.core import ckeditor_config  # noqa: PLC0415

        if not hasattr(settings, "CKEDITOR_5_CONFIGS"):
            settings.CKEDITOR_5_CONFIGS = {}
        if "ddm_ckeditor" not in settings.CKEDITOR_5_CONFIGS:
            settings.CKEDITOR_5_CONFIGS["ddm_ckeditor"] = ckeditor_config.ddm_ckeditor
        if "ddm_ckeditor_temp_func" not in settings.CKEDITOR_5_CONFIGS:
            settings.CKEDITOR_5_CONFIGS["ddm_ckeditor_temp_func"] = (
                ckeditor_config.ddm_ckeditor_temp_func
            )
