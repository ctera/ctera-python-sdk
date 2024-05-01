import logging
from ..common.utils import tcp_connect


def test(Portal):
    tcp_connect(Portal.host(), Portal.port())
    logging.getLogger('cterasdk.core').debug('Trying to obtain Portal public info.')
    response = Portal.public_info()
    logging.getLogger('cterasdk.core').debug('Successfully obtained Portal public info. %s',
                                             {'version': response.version, 'name': response.name})
    return response
