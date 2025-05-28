import cterasdk.settings
from ..services import AsyncManagement
from ..endpoints import EndpointBuilder
from ...clients import clients
from .. import authenticators
from ...lib.session.edge import Session
from ...asynchronous.edge import login, files


class Clients:

    def __init__(self, edge):
        self.api = edge.default.clone(clients.AsyncAPI, EndpointBuilder.new(edge.base, '/admingui/api'))
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

    def __init__(self, host=None, port=None, https=True, *, base=None):
        super().__init__(host, port, https, base, cterasdk.settings.edge.asyn.settings)
        self._ctera_session = Session(self.host())
        self._ctera_clients = Clients(self)
        self.files = files.FileBrowser(self)

    @property
    def v1(self):
        return self.clients.v1

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
