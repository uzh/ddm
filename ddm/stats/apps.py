from django.apps import AppConfig
from django.core import checks

from ddm.stats.checks import check_dependencies


class DdmStatsConfig(AppConfig):
    name = 'ddm.stats'
    label = 'ddmstats'
    verbose_name = 'DDM Stats'

    def ready(self):
        checks.register(check_dependencies, checks.Tags.admin)
