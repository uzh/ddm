from django.views.decorators.debug import sensitive_variables
from rest_framework.fields import empty


class SerializerDecryptionMixin:
    """
    Allows to pass the secret for the decryption of super secret projects to
    the serializer on init.  # TODO: Improve description.
    """
    @sensitive_variables()
    def __init__(self, instance=None, data=empty, decryptor=None, **kwargs):
        self.decryptor = decryptor
        self.secret = kwargs.pop('secret', None)
        super().__init__(instance=instance, data=data, **kwargs)

    @sensitive_variables()
    def get_data(self, obj):
        if not self.secret:
            self.secret = obj.project.secret_key
        return obj.get_decrypted_data(self.secret, obj.project.get_salt(), self.decryptor)
