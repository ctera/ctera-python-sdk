import logging
from ..exceptions import CTERAException
from ..common.utils import tcp_connect


def test(Edge):
    tcp_connect(Edge.host(), Edge.port())
    logging.getLogger('cterasdk.edge').debug('Trying to obtain login info.')
    response = Edge.api.get('/nosession/logininfo')
    if response is not None:
        logging.getLogger('cterasdk.edge').debug('Successfully obtained login info. %s', {'hostname': response.hostname})
        return response
    raise CTERAException('Could not obtain login info for device {host}:{port}.')
