import copy

from ..common import Object
from ..common.utils import Version


class SessionStatus:
    Initializing = 'Initializing'
    Inactive = 'Inactive'
    Active = 'Active'


class SessionUser(Object):
    def __init__(self, name):
        self.name = name


class SessionHostType:
    Edge = 'Edge Filer'
    Portal = 'Portal'
    Agent = 'Agent'


class SessionBase(Object):

    def __init__(self, host, host_type):
        self.host = host
        self.host_type = host_type
        self.status = SessionStatus.Inactive
        self.user = None
        self.version = None

    def set_version(self, version):
        self.version = Version(version)

    def start_local_session(self, CTERA_Host):
        self.status = SessionStatus.Initializing
        self._do_start_local_session(CTERA_Host)
        self.status = SessionStatus.Active

    def _do_start_local_session(self, CTERA_Host):
        raise NotImplementedError("Subclass must implement the _do_start_local_session method")

    def terminate(self):
        self._do_terminate()
        self.status = SessionStatus.Inactive
        self.user = None

    def _do_terminate(self):
        raise NotImplementedError("Subclass must implement the _do_terminate method")

    def initializing(self):
        return self.status == SessionStatus.Initializing

    def authenticated(self):
        return self.status == SessionStatus.Active

    @property
    def active(self):
        return self.status == SessionStatus.Active

    def tenant(self):
        return self.user.tenant if self.user else None

    def whoami(self):
        session = copy.deepcopy(self)
        session.version = str(session.version)
        print(session)
