from .. import invitation
from ...clients import clients
from ..endpoints import EndpointBuilder
from .core import Portal
from ...core import files
from ...core.invitation import login


class Invitation(Portal):

    def __enter__(self):
        self.login()
        return self

    def __init__(self, host, port, invite):
        super().__init__(host, port)
        self.invite = invite
        self.clients.api = self.default.clone(clients.API, EndpointBuilder.new(self.base,
                                                                               self.context, f'/portalInvitation/share/{invite}'))
        self.clients.io._webdav = self.default.clone(clients.WebDAV, EndpointBuilder.new(self.base,
                                                                                         self.context, f'/webdav/share/{invite}'))
        self.clients.io._upload = self.default.clone(clients.Upload, EndpointBuilder.new(self.base,
                                                                                         self.context, f'/upload/share/{invite}'))
        self.files = files.InvitationBrowser(self)
        self.details = None

    @property
    def context(self):
        return 'invitations'

    def _authenticator(self, url):  # pylint: disable=unused-argument
        return True

    def login(self):
        super().login('share', self.invite)
        self.details = self.files.details()

    @property
    def uri(self):
        return invitation.uri(self)

    @property
    def _login_object(self):
        return login.Login(self)

    @staticmethod
    def from_uri(uri):
        host, port, invite = invitation.validate(uri)
        return Invitation(host, port, invite)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.logout()
        return super().__exit__(exc_type, exc_value, exc_tb)
