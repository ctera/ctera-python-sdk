from ..common import Object


class SessionStatus:
    Initializing = 'Initializing'
    Inactive = 'Inactive'
    Active = 'Active'


class SessionUser(Object):
    def __init__(self, name, tenant=None, role=None):
        self.name = name
        self.tenant = tenant
        self.role = role


class SessionBase(Object):

    def __init__(self, host):
        self.host = host
        self.status = SessionStatus.Inactive
        self.user = None

    def start_local_session(self, ctera_host):
        self.status = SessionStatus.Initializing
        self._do_start_local_session(ctera_host)
        self.status = SessionStatus.Active

    def _do_start_local_session(self, ctera_host):
        raise NotImplementedError("Implementing class must implement the _do_start_local_session method")

    def terminate(self):
        self._do_terminate()
        self.status = SessionStatus.Inactive
        self.user = None

    def _do_terminate(self):
        raise NotImplementedError("Implementing class must implement the _do_terminate method")

    def tenant(self):
        return self.user.tenant if self.user else None

    def initializing(self):
        return self.status == SessionStatus.Initializing

    def authenticated(self):
        return self.status == SessionStatus.Active

    def whoami(self):
        print(self)
