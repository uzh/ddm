from ddm import VERSION as ddm_version


def add_ddm_version(request):
    return {'ddm_version': 'DDM v' + ddm_version}
