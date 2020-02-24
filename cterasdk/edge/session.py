import logging

from ..common import Object


def inactive_session(Gateway):
    session = InactiveSession(Gateway.host())
    Gateway.register_session(session)


def start_local_session(Gateway, host, user):
    session = LocalSession(host, user)
    Gateway.register_session(session)


def start_remote_session(Gateway, Portal):
    host = Gateway.host()
    remote_session = Portal.session()
    user = remote_session.user.name
    remote_from = remote_session.host
    tenant = remote_session.current_tenant
    session = RemoteSession(host, user, remote_from, tenant)
    Gateway.register_session(session)


def terminate(Gateway):
    session = Gateway.session()
    if session.local():
        logging.getLogger().debug('Terminating local session. %s', {'host': session.target_host(), 'user': session.username()})
        inactive_session(Gateway)
    elif session.remote():
        logging.getLogger().debug(
            'Terminating remote session. %s',
            {'host': session.target_host(), 'tenant': session.tenant(), 'user': session.username()}
        )
        session.disable_remote_access()


class SessionStatus:
    Inactive = 'Inactive'
    Active = 'Active'


class SessionType:
    Local = 'local'
    Remote = 'remote'


class Session(Object):

    def __init__(self, host, session_type, status):
        self.host = host
        self.connection = Object()
        self.connection.type = session_type
        self.status = status

    def target_host(self):
        return self.host

    def local(self):
        return self.connection.type == SessionType.Local

    def remote(self):
        return self.connection.type == SessionType.Remote

    def authenticated(self):
        return self.status == SessionStatus.Active


class InactiveSession(Session):

    def __init__(self, host):
        super().__init__(host, SessionType.Local, SessionStatus.Inactive)


class ActiveSession(Session):

    def __init__(self, host, session_type, user):
        super().__init__(host, session_type, SessionStatus.Active)
        self.user = Object()
        self.user.name = user

    def username(self):
        return self.user.name


class LocalSession(ActiveSession):

    def __init__(self, host, user):
        super().__init__(host, SessionType.Local, user)


class RemoteSession(ActiveSession):

    def __init__(self, host, user, remote_from, tenant):
        super().__init__(host, SessionType.Remote, user)
        self.connection.remote_from = remote_from
        self.connection.remote_access = False
        self.user.tenant = tenant

    def enable_remote_access(self):
        self.connection.remote_access = True

    def disable_remote_access(self):
        self.connection.remote_access = False

    def remote_access(self):  # pylint: disable=method-hidden
        return self.connection.remote_access

    def remote_from(self):  # pylint: disable=method-hidden
        return self.connection.remote_from

    def tenant(self):  # pylint: disable=method-hidden
        return self.user.tenant
