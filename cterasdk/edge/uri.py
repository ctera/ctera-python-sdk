import logging

from ..exception import CTERAException


def api(Gateway):
    session = Gateway.session()
    if session.local():                             # direct access, via IP, hostname or FQDN
        return local(Gateway._baseurl())  # pylint: disable=protected-access

    if session.remote():
        baseurl = Gateway._Portal._baseurl()  # pylint: disable=protected-access
        device = Gateway.host()
        if session.remote_access():
            return remote_access(baseurl, device)   # remote: Gateway.remote_access()

        tenant = session.tenant()
        return remote(baseurl, tenant, device)  # remote, without a Gateway session

    logging.getLogger().error('Invalid connection type.')
    raise CTERAException('Invalid connection type', session)


def local(baseurl):
    return '%s/admingui/api' % (baseurl)


def remote(baseurl, tenant, device):
    return '%s/devicecmdnew/%s/%s/' % (baseurl, tenant, device)


def remote_access(baseurl, device):
    return '%s/devices/%s/admingui/api' % (baseurl, device)


def files(Gateway):
    session = Gateway.session()
    if session.local():
        baseurl = Gateway._baseurl()  # pylint: disable=protected-access
        return '%s/localFiles' % (baseurl)

    if session.remote():
        if session.remote_access():
            baseurl = Gateway._Portal._baseurl()  # pylint: disable=protected-access
            device = Gateway.host()
            return '%s/devices/%s/localFiles' % (baseurl, device)
    raise CTERAException('Invalid connection type', session)
