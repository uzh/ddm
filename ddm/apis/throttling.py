from django.conf import settings
from django.http import HttpRequest
from django.views import View
from rest_framework.throttling import SimpleRateThrottle

from ddm.auth.models import ProjectAccessToken

DEFAULT_PROJECT_API_THROTTLE_RATE = "100/min"


class ProjectTokenRateThrottle(SimpleRateThrottle):
    """Per-token rate limit for the project-token-authenticated API endpoints.

    Requests that authenticated via SessionAuthentication (request.auth is None)
    aren't throttled by this class.

    Rate is read from DDM_SETTINGS (overridable without a code change),
    falling back to DEFAULT_PROJECT_API_THROTTLE_RATE.
    """

    scope = "project_token"

    def __init__(self) -> None:
        self.rate = getattr(settings, "DDM_SETTINGS", {}).get(
            "PROJECT_API_THROTTLE_RATE", DEFAULT_PROJECT_API_THROTTLE_RATE
        )
        self.num_requests, self.duration = self.parse_rate(self.rate)

    def get_cache_key(self, request: HttpRequest, view: View) -> str | None:
        token = getattr(request, "auth", None)
        if not isinstance(token, ProjectAccessToken):
            return None

        return self.cache_format % {"scope": self.scope, "ident": token.pk}
