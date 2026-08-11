import cterasdk.settings
from ..services import AsyncManagement
from ..endpoints import EndpointBuilder
from ...clients import clients
from .. import authenticators
from ...lib.session.edge import Session
from ...asynchronous.edge import login, files


class Clients:

    def __init__(self, edge, core):
        if core:
            edge.session().start_remote_session(core.session())
            self.migrate = clients.RestrictedAPI('migrate')
            self.api = edge.default.clone(clients.AsyncAPI, EndpointBuilder.new(edge.base), authenticator=lambda *_: True)
            self.stats = clients.RestrictedAPI('stats')
            self.io = clients.RestrictedAPI('io')
        else:
            self.migrate = edge.default.clone(clients.AsyncMigrate, EndpointBuilder.new(edge.base, '/migration/rest/v1'))
            self.api = edge.default.clone(clients.AsyncAPI, EndpointBuilder.new(edge.base, '/admingui/api'))
            self.stats = edge.default.clone(clients.AsyncJSON, EndpointBuilder.new(edge.base, '/stats'))
            self.io = IO(edge)


class IO:

    def __init__(self, edge):
        self._edge = edge
        self._webdav = edge.default.clone(clients.AsyncWebDAV, EndpointBuilder.new(edge.base, '/localFiles'))

    @property
    def download(self):
        return self._webdav.download

    @property
    def download_zip(self):
        return self._edge.default.form_data  # pylint: disable=protected-access

    @property
    def upload(self):
        return self._edge.default.form_data  # pylint: disable=protected-access

    @property
    def propfind(self):
        return self._webdav.propfind

    @property
    def mkdir(self):
        return self._webdav.mkcol

    @property
    def copy(self):
        return self._webdav.copy

    @property
    def move(self):
        return self._webdav.move

    @property
    def delete(self):
        return self._webdav.delete


class AsyncEdge(AsyncManagement):

    def __init__(self, host=None, port=None, https=True, core=None, *, base=None):
        super().__init__(host, port, https, base, cterasdk.settings.edge.asyn.settings, core=core)
        self._ctera_session = Session(self.host())
        self._ctera_clients = Clients(self, core)
        self.files = files.FileBrowser(self)

    @property
    def api(self):
        return self.clients.api

    @property
    def io(self):
        return self.clients.io

    @property
    def _login_object(self):
        return login.Login(self)

    def _authenticator(self, url):
        return authenticators.edge(self.session(), url)

    @property
    def _omit_fields(self):
        return super()._omit_fields + ['files']
