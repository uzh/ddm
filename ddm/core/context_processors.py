from django.http import HttpRequest

from ddm import VERSION as DDM_VERSION


def add_ddm_version(request: HttpRequest) -> dict[str, str]:
    return {"ddm_version": "DDM v" + DDM_VERSION}
