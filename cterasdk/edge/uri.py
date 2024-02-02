import logging

from ..common import parse_base_object_ref
from ..exception import CTERAException


def api(Gateway):
    session = Gateway.session()
    if session.local():                             # direct access, via IP, hostname or FQDN
        return local(Gateway.baseurl())

    if session.remote():
        baseurl = Gateway._Portal.base_portal_url  # pylint: disable=protected-access
        device = Gateway.host()
        base_object_ref = parse_base_object_ref(Gateway.portal)
        return remote(baseurl, base_object_ref.name, device)  # remote, without a Gateway session

    logging.getLogger().error('Invalid connection type.')
    raise CTERAException('Invalid connection type', session)


def local(baseurl):
    return f'{baseurl}/admingui/api'


def remote(baseurl, tenant, device):
    return f'{baseurl}/devicecmdnew/{tenant}/{device}/'


def files(Gateway):
    return Gateway.baseurl()
