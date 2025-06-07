import logging
from ..exceptions import CTERAException
from ..common.utils import tcp_connect


logger = logging.getLogger('cterasdk.edge')


def test(Edge):
    tcp_connect(Edge.host(), Edge.port())
    logger.debug('Trying to obtain login info.')
    response = Edge.api.get('/nosession/logininfo')
    if response is not None:
        logger.debug('Successfully obtained login info for: %s', response.hostname)
        return response
    raise CTERAException('Could not obtain login info for device (host={host}, port={port}).')
