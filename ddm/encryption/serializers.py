from typing import Any

from django.views.decorators.debug import sensitive_variables
from rest_framework.fields import empty

from ddm.encryption.models import Decryption


class SerializerDecryptionMixin:
    """Enables decryption of encrypted project data during serialization.

    Used by DataDonation and QuestionnaireResponse models.
    Accepts a `secret` and `decryptor` on init (falling back to
    `obj.project.secret_key` if no secret is given). `get_data()` returns
    the decrypted value and is meant to back a `SerializerMethodField`.

    Note: Both methods are wrapped in `@sensitive_variables()` since `secret`/
    `decryptor` are sensitive and shouldn't appear in tracebacks.
    """

    @sensitive_variables()
    def __init__(
        self,
        instance: Any = None,  # noqa: ANN401
        data: Any = empty,  # noqa: ANN401
        decryptor: Decryption | None = None,
        **kwargs,
    ) -> None:
        self.decryptor = decryptor
        self.secret = kwargs.pop("secret", None)
        super().__init__(instance=instance, data=data, **kwargs)

    @sensitive_variables()
    def get_data(self, obj: Any) -> Any:  # noqa: ANN401
        if not self.secret:
            self.secret = obj.project.secret_key

        # Single-slot cache: avoids decrypting the same object's data twice
        # when a subclass calls get_data() from more than one field (e.g.
        # ResponseSerializerWithSnapshot uses it for both response_data and
        # questionnaire_snapshot). Only needs to survive across the field
        # evaluations for one object, so it's not a growing/unbounded cache.
        cached = getattr(self, "_decrypted_cache", None)
        if cached is not None and cached[0] == obj.pk:
            return cached[1]

        value = obj.get_decrypted_data(
            self.secret, obj.project.get_salt(), self.decryptor
        )
        self._decrypted_cache = (obj.pk, value)
        return value
