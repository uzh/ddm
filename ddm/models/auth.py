import binascii
import os

from django.db import models
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class CustomToken(models.Model):
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

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    def has_expired(self):
        """ Returns False if token has expired. """
        if self.expiration_date is not None and timezone.now() > self.expiration_date:
            return True
        else:
            return False


class CustomTokenAuthenticator(TokenAuthentication):
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
    model = CustomToken

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('project').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if token.has_expired():
            raise exceptions.AuthenticationFailed('Token has expired. You can create a new one in the admin backend.')

        return token.project.owner.user, token  # TODO: Check if this user return makes sense.
