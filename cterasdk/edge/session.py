import logging

from ..common import Object
from ..lib.session_base import SessionBase, SessionUser, SessionStatus


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


class Session(SessionBase):

    def __init__(self, host):
        super().__init__(host)
        self.connection = SessionConnection(SessionType.Local)

    def _do_start_local_session(self, ctera_host):
        user = ctera_host.get('currentuser')
        self._activate(SessionType.Local, user)

    def start_remote_session(self, remote_session):
        self._activate(SessionType.Remote, remote_session.user.name, tenant=remote_session.user.tenant, remote_from=remote_session.host)
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

    def _activate(self, session_type, user, tenant=None, remote_from=None):
        self.user = SessionUser(user, tenant=tenant)
        self.connection = SessionConnection(session_type, remote_from=remote_from)
