import cterasdk.settings
from ..services import CTERA, client_settings
from ..endpoints import EndpointBuilder
from ...clients.asynchronous import clients

from .. import authenticators

from ...lib.session.core import Session

from ...asynchronous.core import login
from ...asynchronous.core import cloudfs
from ...asynchronous.core import notifications
from ...asynchronous.core import users


class Clients:

    def __init__(self, core):
        self.v1 = V1(core)
        self.v2 = V2(core)
        self.io = IO(core)


class V1:

    def __init__(self, core):
        session = core._generic._async_session
        self.api = clients.AsyncAPI(EndpointBuilder.new(core.base, core.context, '/api'), session, core._authenticator,
                                    core._generic._client_settings)


class V2:

    def __init__(self, core):
        session = core._generic._async_session
        self.api = clients.AsyncJSON(EndpointBuilder.new(core.base, core.context, '/v2/api'), session,
                                     core._authenticator, core._generic._client_settings)


class IO:

    def __init__(self, core):
        self.webdav = WebDAV(core)


class WebDAV:

    def __init__(self, core):
        session = core._generic._async_session
        self._webdav = clients.AsyncWebDAV(EndpointBuilder.new(core.base, core.context, '/webdav'), session, core._authenticator,
                                           core._generic._client_settings)

    @property
    def download(self):
        return self._webdav.get


class AsyncPortal(CTERA):

    async def __aenter__(self):
        return self

    def __init__(self, host, port=None, https=True):
        super().__init__(host, port, https, base=None)
        self._generic = clients.AsyncClient(EndpointBuilder.new(self.base), authenticator=self._authenticator,
                                            client_settings=client_settings(cterasdk.settings.sessions.metadata_connector))
        self._ctera_session = Session(self.host(), self.context)
        self._ctera_clients = Clients(self)

        self.cloudfs = cloudfs.CloudFS(self)
        self.notifications = notifications.Notifications(self)
        self.users = users.Users(self)

    @property
    def v1(self):
        return self.clients.v1

    @property
    def v2(self):
        return self.clients.v2

    @property
    def io(self):
        return self.clients.io

    async def login(self, username, password):
        self._before_login()
        await self._login_object.login(username, password)
        await self._ctera_session.async_start_session(self)
        self._after_login()

    async def logout(self):
        if self._ctera_session.connected:
            await self._login_object.logout()
            self._ctera_session.stop_session()
        await self._generic.close()

    @property
    def _login_object(self):
        return login.Login(self)

    def _authenticator(self, url):
        return authenticators.core(self.session(), url, self.context)

    async def __aexit__(self, exc_type, exc, tb):
        await self._generic.close()


class AsyncGlobalAdmin(AsyncPortal):

    @property
    def context(self):
        return 'admin'


class AsyncServicesPortal(AsyncPortal):

    @property
    def context(self):
        return 'ServicesPortal'
