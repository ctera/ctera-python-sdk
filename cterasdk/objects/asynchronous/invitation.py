from .. import invitation
from ...clients import clients
from ..endpoints import EndpointBuilder
from .core import AsyncPortal
from ..asynchronous.core import files
from ...asynchronous.core.invitation import login


class AsyncInvitation(AsyncPortal):

    async def __aenter__(self):
        await self.login()
        return self

    def __init__(self, host, port, invite):
        super().__init__(host, port)
        self.invite = invite
        self.clients.v1.api = self.default.clone(clients.AsyncAPI, EndpointBuilder.new(self.base,
                                                                                       self.context, f'/portalInvitation/share/{invite}'))
        self.clients.io._webdav = self.default.clone(clients.AsyncWebDAV, EndpointBuilder.new(self.base,
                                                                                              self.context, f'/webdav/share/{invite}'))
        self.clients.io._upload = self.default.clone(clients.AsyncUpload, EndpointBuilder.new(self.base,
                                                                                              self.context, f'/upload/share/{invite}'))
        self.files = files.InvitationBrowser(self)
        self.details = None

    @property
    def context(self):
        return 'invitations'

    def _authenticator(self, url):  # pylint: disable=unused-argument
        return True

    async def login(self):  # pylint: disable=arguments-differ
        await super().login('share', self.invite)
        self.details = await self.files.details()

    @property
    def uri(self):
        return f'{self.clients.v1.ctera.baseurl}/?share={self.invite}'

    @property
    def _login_object(self):
        return login.Login(self)

    @staticmethod
    def from_uri(uri):
        host, port, invite = invitation.validate(uri)
        return AsyncInvitation(host, port, invite)

    async def __aexit__(self, exc_type, exc, tb):
        await self.logout()
        return await super().__aexit__(exc_type, exc, tb)
