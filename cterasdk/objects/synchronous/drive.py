import cterasdk.settings
from ...clients import clients
from ..services import Management
from ..endpoints import EndpointBuilder
from ...lib.session.edge import Session
from ...edge import backup, cli, logs, services, support, sync


class Clients:

    def __init__(self, drive, Portal):
        if Portal:
            drive._Portal = Portal
            drive.default.close()
            drive._ctera_session.start_remote_session(Portal.session())
            self.api = Portal.default.clone(clients.API, EndpointBuilder.new(drive.base), authenticator=lambda *_: True)
        else:
            self.api = drive.default.clone(clients.API, EndpointBuilder.new(drive.base, '/admingui/api'))


class Drive(Management):

    def __init__(self, host=None, port=None, https=True, Portal=None, *, base=None):
        super().__init__(host, port, https, base, cterasdk.settings.drive.syn.settings)
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

    @property
    def _omit_fields(self):
        return super()._omit_fields + ['backup', 'cli', 'logs', 'services', 'support', 'sync']
