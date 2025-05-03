import cterasdk.settings
from ..services import CTERA, client_settings
from ..endpoints import EndpointBuilder
from ...clients.asynchronous import clients

from .. import authenticators

from ...lib.session.core import Session

from ...asynchronous.core import files
from ...asynchronous.core import login
from ...asynchronous.core import cloudfs
from ...asynchronous.core import notifications
from ...asynchronous.core import portals
from ...asynchronous.core import settings
from ...asynchronous.core import users


class Clients:

    def __init__(self, core):
        self.v1 = V1(core)
        self.v2 = V2(core)
        self.io = IO(core)


class V1:

    def __init__(self, core):
        self.ctera = core.default.clone(clients.AsyncExtended, EndpointBuilder.new(core.base, core.context))
        self.api = core.default.clone(clients.AsyncAPI, EndpointBuilder.new(core.base, core.context, '/api'))


class V2:

    def __init__(self, core):
        self.api = core.default.clone(clients.AsyncJSON, EndpointBuilder.new(core.base, core.context, '/v2/api'))


class IO:

    def __init__(self, core):
        self._folders = core.default.clone(clients.AsyncFolders, EndpointBuilder.new(core.base, core.context, '/folders/folders'))
        self._upload = core.default.clone(clients.AsyncUpload, EndpointBuilder.new(core.base, core.context, '/upload/folders'))
        self._webdav = core.default.clone(clients.AsyncWebDAV, EndpointBuilder.new(core.base, core.context, '/webdav'))

    @property
    def upload(self):
        return self._upload.upload

    @property
    def download(self):
        return self._webdav.get

    @property
    def download_zip(self):
        return self._folders.download_zip

    @property
    def builder(self):
        return self._webdav._builder  # pylint: disable=protected-access


class AsyncPortal(CTERA):

    async def __aenter__(self):
        return self

    def __init__(self, host, port=None, https=True):
        super().__init__(host, port, https, base=None)
        self._default = clients.AsyncClient(EndpointBuilder.new(self.base),
                                            settings=client_settings(cterasdk.settings.sessions.metadata_connector),
                                            authenticator=self._authenticator)
        self._ctera_session = Session(self.host(), self.context)
        self._ctera_clients = Clients(self)

        self.cloudfs = cloudfs.CloudFS(self)
        self.files = files.CloudDrive(self)
        self.notifications = notifications.Notifications(self)
        self.settings = settings.Settings(self)
        self.users = users.Users(self)

    @property
    def default(self):
        return self._default

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
        await self.default.close()

    @property
    def _login_object(self):
        return login.Login(self)

    def _authenticator(self, url):
        return authenticators.core(self.session(), url, self.context)

    async def __aexit__(self, exc_type, exc, tb):
        await self.default.close()


class AsyncGlobalAdmin(AsyncPortal):

    def __init__(self, host, port=None, https=True):
        super().__init__(host, port, https)
        self.portals = portals.Portals(self)

    @property
    def context(self):
        return 'admin'

    async def impersonate(self, username, tenant):
        """
        Impersonate a Portal user

        :param str username: Username
        :param str tenant: Tenant
        """
        ctera_ticket = await self.users.generate_ticket(username, tenant)
        user = AsyncServicesPortal(f'{tenant}.{await self.settings.global_settings.dns_suffix}', self.port())
        await user.sso(ctera_ticket)
        return user


class AsyncServicesPortal(AsyncPortal):

    @property
    def context(self):
        return 'ServicesPortal'

    async def sso(self, ctera_ticket):
        """
        Login using a Portal ticket

        :param str ctera_ticket: SSO Ticket.
        """
        await self._login_object.sso(ctera_ticket)
        await self._ctera_session.async_start_session(self)
        await self.v1.api.web_session()
