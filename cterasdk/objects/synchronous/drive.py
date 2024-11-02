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
            drive.default.close()
            drive._ctera_session.start_remote_session(Portal.session())
            self.api = drive.default.clone(clients.API, EndpointBuilder.new(drive.base), authenticator=lambda *_: True)
        else:
            self.api = drive.default.clone(clients.API, EndpointBuilder.new(drive.base, '/admingui/api'))


class Drive(Management):

    def __init__(self, host=None, port=None, https=True, Portal=None, *, base=None):
        super().__init__(host, port, https, base=base)
        self._ctera_session = Session(self.host())
        self._ctera_clients = Clients(self, Portal)

        self.backup = backup.Backup(self)
        self.cli = cli.CLI(self)
        self.logs = logs.Logs(self)
        self.services = services.Services(self)
        self.support = support.Support(self)
        self.sync = sync.Sync(self)

    @property
    def api(self):
        return self.clients.api

    @property
    def _session_id_key(self):
        return '_cteraSessionId_'

    @property
    def _login_object(self):
        raise NotImplementedError("Logins to the 'Drive App' are not enabled.")
