from ..clients.synchronous import clients
from .services import CTERA
from .endpoints import EndpointBuilder


class Clients:

    def __init__(self, core):
        session = core._generic._async_session
        self._v2 = clients.AsyncJSON(EndpointBuilder.new(core.base, core.context, '/v2/api'), session, core._authenticator)

    
class MetadataConnector(CTERA):

    def __init__(self, host, port=None, https=True):
        super().__init__(host, port, https, base=None)
        self._ctera_clients = Clients(self)

    @property
    def v2(self):
        return self._ctera_clients._v2