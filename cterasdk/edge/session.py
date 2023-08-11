import logging

from ..common import Object
from ..lib.session_base import SessionBase, SessionUser, SessionStatus, SessionHostType


class SessionType:
    Local = 'local'
    Remote = 'remote'


class SessionConnection(Object):
    def __init__(self, session_type, remote_from=None):
        self.type = session_type
        if session_type == SessionType.Remote:
            self.remote_from = remote_from
            self.remote_access = False
        else:
            self.remote_from = None
            self.remote_access = None


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
        user = CTERA_Host.get('/currentuser').username
        self.set_version(CTERA_Host.get('/status/device/runningFirmware'))
        self.user = LocalUser(user)
        self.connection = SessionConnection(SessionType.Local)

    def start_remote_session(self, remote_session):
        self.user = RemoteUser(remote_session.user.name, remote_session.user.tenant)
        self.connection = SessionConnection(SessionType.Remote, remote_session.host)
        self.status = SessionStatus.Active

    def _do_terminate(self):
        if self.local():
            logging.getLogger().debug('Terminating local session. %s', {'host': self.host, 'user': self.user.name})
            self.connection = SessionConnection(SessionType.Local)
        elif self.remote():
            logging.getLogger().debug(
                'Terminating remote session. %s',
                {'host': self.host, 'tenant': self.user.tenant, 'user': self.user.name}
            )
            self.disable_remote_access()

    def local(self):
        return self.connection.type == SessionType.Local

    def remote(self):
        return self.connection.type == SessionType.Remote

    def enable_remote_access(self):
        self.connection.remote_access = True

    def disable_remote_access(self):
        self.connection.remote_access = False

    def remote_access(self):  # pylint: disable=method-hidden
        return self.connection.remote_access

    def remote_from(self):  # pylint: disable=method-hidden
        return self.connection.remote_from

    def tenant(self):
        return self.user.tenant if isinstance(self.user, RemoteUser) else None
