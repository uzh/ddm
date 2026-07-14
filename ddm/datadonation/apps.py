from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DDMDataDonationConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "ddm.datadonation"
    label = "ddm_datadonation"
    verbose_name = _("DDM Data Donation")

    def ready(self) -> None:
        import ddm.datadonation.signals  # noqa: F401, PLC0415
