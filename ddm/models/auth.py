import binascii
import os

from ddm.models.logs import EventLogEntry
from django.db import models
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header


class ProjectAccessToken(models.Model):
    """
    Custom authorization token that is linked to a DonationProject.
    Adapted from the Token model as implemented in rest_framework.authtoken.models.Token.
    """
    key = models.CharField(max_length=40, primary_key=True)
    project = models.OneToOneField(
        'DonationProject', related_name='donation_project',
        on_delete=models.CASCADE, verbose_name='Donation Project'
    )
    created = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        EventLogEntry.objects.create(
            project=self.project,
            description='Access Token Deleted'
        )
        super().delete(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    def has_expired(self):
        """ Returns False if token has expired. """
        return self.expiration_date is not None and timezone.now() > self.expiration_date


class ProjectTokenAuthenticator(TokenAuthentication):
    """
    Custom implementation of the rest_framework.authentication.TokenAuthentication
    method that does not require a token to be related to a user. Instead, the
    custom model requires a token to be related to a DonationProject.
    Furthermore, the custom method supports token expiration.

    From original description:
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    model = ProjectAccessToken

    def authenticate(self, request):
        """
        Adopted from parent model. Added that request is passed to
        authenticate_credentials in order to check if the requested project
        matches the token.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            project_pk = request.parser_context['kwargs'].get('pk', None)
            project_pk = int(project_pk)
        except ValueError:
            msg = 'Invalid project identifier provided.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token, project_pk)

    def authenticate_credentials(self, key, project_pk):
        model = self.get_model()
        try:
            token = model.objects.select_related('project').get(key=key)
        except model.DoesNotExist:
            msg = 'Invalid token.'
            raise exceptions.AuthenticationFailed(msg)

        if token.has_expired():
            msg = 'Token has expired. You can create a new one in the admin backend.'
            raise exceptions.AuthenticationFailed(msg)

        if token.project.pk != project_pk:
            msg = 'The provided token does not belong to the requested project.'
            raise exceptions.AuthenticationFailed(msg)

        return token.project.owner.user, token
