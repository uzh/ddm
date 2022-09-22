import re

from django.conf import settings

from ddm.models.core import DonationProject, ResearchProfile


def email_is_valid(email_string):
    """
    Check if an email address complies with the pattern specified in
    DDM_SETTINGS['EMAIL_PERMISSION_CHECK'].
    If this setting is not defined, returns True.
    """
    if hasattr(settings, 'DDM_SETTINGS'):
        if 'EMAIL_PERMISSION_CHECK' in settings.DDM_SETTINGS:
            match = re.match(settings.DDM_SETTINGS['EMAIL_PERMISSION_CHECK'],
                             email_string)
            if not match:
                return False
    return True


def user_is_permitted(user):
    """
    Check if a user has access permission.
    """
    if user.is_superuser:
        return True
    elif user.is_authenticated:
        profile = ResearchProfile.objects.filter(user=user).first()
        if profile:
            if profile.ignore_email_restriction:
                return True
        if email_is_valid(user.email):
            return True
    return False


def user_is_owner(user, project_pk):
    """
    Check if a given user is the owner of the project with the ID provided in
    project_pk.
    """
    donation_project = DonationProject.objects.get(pk=project_pk)
    if donation_project.owner.user == user:
        return True
    else:
        return False
