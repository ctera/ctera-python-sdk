from ..aio_client import clients
from .services import CTERA
from .endpoints import EndpointBuilder

from . import authenticators

from ..edge import backup
from ..edge import cli
from ..edge import logs
from ..edge import services
from ..edge import session
from ..edge import support
from ..edge import sync
from ..edge import uri


class Drive(CTERA):

    def __init__(self, host=None, port=None, https=None, *, base=None):
        super().__init__(host, port, https, base=base)
        async_session = self._generic._async_session
        self._ctera_session = session.Session(self.host())
        self._management = clients.Management(EndpointBuilder.new(self.base, '/admingui/api'), async_session, self._authenticator)

        self.backup = backup.Backup(self)
        self.cli = cli.CLI(self)
        self.logs = logs.Logs(self)
        self.services = services.Services(self)
        self.support = support.Support(self)
        self.sync = sync.Sync(self)

    @property
    def management(self):
        return self._management
    
    @property
    def _session_id_key(self):
        return '_cteraSessionId_'
    
    def _authenticator(self, url):
        return True
    
    @property
    def _login_object(self):
        raise NotImplementedError("Logins to the 'Drive App' are not enabled.")