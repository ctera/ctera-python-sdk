import logging

from ..common import Object
from ..lib.session_base import SessionBase, SessionUser, SessionStatus, SessionHostType


class SessionType:
    Local = 'local'
    Remote = 'remote'


class SessionConnection(Object):
    def __init__(self, session_type, remote_from=None):
        self.type = session_type
        self.remote_from = remote_from if session_type == SessionType.Remote else None


class LocalUser(SessionUser):
    """Local Session Object"""


class RemoteUser(SessionUser):
    """Remote Session Object"""

    def __init__(self, name, tenant):
        super().__init__(name)
        self.tenant = tenant


class Session(SessionBase):

    def __init__(self, host):
        super().__init__(host, SessionHostType.Edge)
        self.connection = SessionConnection(SessionType.Local)

    def _do_start_local_session(self, CTERA_Host):
        user = CTERA_Host.api.get('/currentuser').username
        self.set_version(CTERA_Host.api.get('/status/device/runningFirmware'))
        self.user = LocalUser(user)
        self.connection = SessionConnection(SessionType.Local)

    def start_remote_session(self, remote_session):
        self.user = RemoteUser(remote_session.user.name, remote_session.user.tenant)
        self.connection = SessionConnection(SessionType.Remote, remote_session.host)
        self.status = SessionStatus.Active

    def _do_terminate(self):
        logging.getLogger('cterasdk.edge').debug('Terminating local session. %s', {'host': self.host, 'user': self.user.name})
        self.connection = SessionConnection(SessionType.Local)

    def local(self):
        return self.connection.type == SessionType.Local

    def remote(self):
        return self.connection.type == SessionType.Remote

    def remote_from(self):  # pylint: disable=method-hidden
        return self.connection.remote_from

    def tenant(self):
        return self.user.tenant if isinstance(self.user, RemoteUser) else None
