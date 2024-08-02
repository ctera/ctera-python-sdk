from ...clients.synchronous import clients
from ..services import Management
from ..endpoints import EndpointBuilder

from ...lib.session.edge import Session

from ...edge import backup
from ...edge import cli
from ...edge import logs
from ...edge import services
from ...edge import support
from ...edge import sync


class Clients:

    def __init__(self, drive, Portal):
        if Portal:
            drive._Portal = Portal
            drive._generic.close()
            drive._ctera_session.start_remote_session(Portal.session())
            self._api = clients.API(EndpointBuilder.new(drive.base), Portal._generic._async_session, lambda *_: True)
        else:
            self._api = clients.API(EndpointBuilder.new(drive.base, '/admingui/api'), drive._generic._async_session, drive._authenticator)


class Drive(Management):

    def __init__(self, host=None, port=None, https=True, Portal=None, *, base=None):
        super().__init__(host, port, https, base=base)
        self._ctera_session = Session(self.host())

        self._initialize(Portal)

        self.backup = backup.Backup(self)
        self.cli = cli.CLI(self)
        self.logs = logs.Logs(self)
        self.services = services.Services(self)
        self.support = support.Support(self)
        self.sync = sync.Sync(self)

    def _initialize(self, Portal):
        if Portal:
            self._generic.close()
            async_session = Portal._generic._async_session  # pylint: disable=protected-access
            self._ctera_session.start_remote_session(Portal.session())
            self._api = clients.API(EndpointBuilder.new(self.base), async_session, lambda *_: True)
        else:
            async_session = self._generic._async_session  # pylint: disable=protected-access
            self._api = clients.API(EndpointBuilder.new(self.base, '/admingui/api'), async_session, self._authenticator)

    @property
    def _session_id_key(self):
        return '_cteraSessionId_'

    @property
    def _login_object(self):
        raise NotImplementedError("Logins to the 'Drive App' are not enabled.")
