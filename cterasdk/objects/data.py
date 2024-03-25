from .services import CTERA
from .endpoints import EndpointBuilder
from ..clients.asynchronous import clients


from ..asynchronous.core import login
from ..asynchronous.core import cloudfs
from ..asynchronous.core import notifications
from ..asynchronous.core import users


class Clients:

    def __init__(self, services):
        self.v1 = V1(services)
        self.v2 = V2(services)


class V1:

    def __init__(self, services):
        session = services._generic._async_session
        self.api = clients.AsyncAPI(EndpointBuilder.new(services.base, services.context, '/api'), session, services._authenticator)


class V2:

    def __init__(self, services):
        session = services._generic._async_session
        self.api = clients.AsyncJSON(EndpointBuilder.new(services.base, services.context, '/v2/api'), session, services._authenticator)


class DataServices(CTERA):

    async def __aenter__(self):
        return self

    def __init__(self, host, port=None, https=True):
        super().__init__(host, port, https, base=None)
        self._generic = clients.AsyncClient(EndpointBuilder.new(self.base), authenticator=self._authenticator)
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

    async def login(self, username, password):
        return await self._login_object.login(username, password)

    async def logout(self):
        await self._login_object.logout()
        await self.clients.v1.api.shutdown()

    @property
    def _login_object(self):
        return login.Login(self)

    @property
    def context(self):
        return 'admin'

    def _authenticator(self, url):
        return True

    async def __aexit__(self, exc_type, exc, tb):
        await self._generic.shutdown()
