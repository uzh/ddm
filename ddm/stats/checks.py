from django.apps import apps
from django.core import checks


def check_dependencies(**kwargs):
    """
    Check that the dependencies of ddm.stats are correctly installed.
    """
    if not apps.is_installed('ddm.stats'):
        return []
    errors = []
    app_dependencies = ['ddm']
    for app_name in app_dependencies:
        if not apps.is_installed(app_name):
            errors.append(
                checks.Error(
                    f'{app_name} must be in INSTALLED_APPS in order to use the '
                    f'ddm stats application.'
                )
            )
    return errors
