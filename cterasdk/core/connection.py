import logging
from ..common.utils import tcp_connect


logger = logging.getLogger('cterasdk.core')


def test(Portal):
    tcp_connect(Portal.host(), Portal.port())
    logger.debug('Trying to obtain Portal public info.')
    response = Portal.public_info()
    logger.debug('Successfully obtained Portal public info. %s', {'version': response.version, 'name': response.name})
    return response
