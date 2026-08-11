import cterasdk.settings
from ..services import AsyncManagement
from ..endpoints import EndpointBuilder
from ...clients import clients
from ...lib.session.edge import Session


class Clients:

    def __init__(self, drive, core):
        if core:
            drive.session().start_remote_session(core.session())
            self.api = core.default.clone(clients.AsyncAPI, EndpointBuilder.new(drive.base), authenticator=lambda *_: True)
        else:
            self.api = drive.default.clone(clients.AsyncAPI, EndpointBuilder.new(drive.base, '/admingui/api'))


class AsyncDrive(AsyncManagement):

    def __init__(self, host=None, port=None, https=True, core=None, *, base=None):
        super().__init__(host, port, https, base, cterasdk.settings.edge.asyn.settings, core=core)
        self._ctera_session = Session(self.host())
        self._ctera_clients = Clients(self, core)

    @property
    def api(self):
        return self.clients.api

    @property
    def _login_object(self):
        raise NotImplementedError("Logins to the 'Drive App' are not enabled.")
