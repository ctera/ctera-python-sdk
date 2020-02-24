from ..client import NetworkHost, CTERAHost
from ..core import connection
from ..core import activation
from ..core import directoryservice
from ..core import enum
from ..core import login
from ..core import whoami
from ..core import query
from ..core import logs
from ..core import portals
from ..core import servers
from ..core import devices
from ..core import session
from ..core import users
from ..core import cloudfs
from ..core import zones
from ..core import files
from ..core import decorator


class Portal(CTERAHost):  # pylint: disable=too-many-public-methods

    def __init__(self, host, port, https):
        super().__init__(host, port, https)
        session.inactive_session(self)

    def test(self):
        connection.test(self)
        return CTERAHost.get(self, self._baseurl(), '/public/publicInfo', params={})

    def login(self, username, password):
        login.login(self, username, password)

    @decorator.authenticated
    def logout(self):
        login.logout(self)

    def whoami(self):
        whoami.whoami(self)

    @decorator.authenticated
    def get(self, path, params=None):
        return super().get(self._api(), path, params if params else {})

    @decorator.authenticated
    def show(self, path):
        super().show(self._api(), path)

    @decorator.authenticated
    def get_multi(self, path, paths):
        return super().get_multi(self._api(), path, paths)

    @decorator.authenticated
    def show_multi(self, paths):
        super().show_multi(self._api(), paths)

    @decorator.update_current_tenant
    @decorator.authenticated
    def put(self, path, value):
        return super().put(self._api(), path, value)

    def form_data(self, path, form_data):
        return super().form_data(self._api(), path, form_data)

    @decorator.authenticated
    def execute(self, path, name, param=None):
        return super().execute(self._api(), path, name, param)

    @decorator.authenticated
    def query(self, path, param):
        return query.query(self, path, param)

    @decorator.authenticated
    def show_query(self, path, param):
        return query.show(self, path, param)

    @decorator.authenticated
    def add(self, path, param):
        return super().add(self._api(), path, param)

    def iterator(self, path, param):
        return query.iterator(self, path, param)

    def local_users(self, include=None):
        return users.local_users(self, include if include else [])

    def add_user(self, username, email, first_name, last_name, password, role=enum.Role.EndUser, company=None, comment=None):
        return users.add(self, username, email, first_name, last_name, password, role, company, comment)

    def delete_user(self, username):
        return users.delete(self, username)

    def domains(self):
        return self.get('/domains')

    def domain_users(self, domain, include=None):
        return users.domain_users(self, domain, include if include else [])

    def fetch(self, tuples):
        return directoryservice.fetch(self, tuples)

    def device(self, name, include=None):
        return devices.device(self, name, include if include else [])

    def filers(self, include=None, allPortals=False, deviceTypes=None):
        return devices.filers(self, include if include else [], allPortals, deviceTypes if deviceTypes else [])

    def agents(self, include=None, allPortals=False):
        return devices.agents(self, include if include else [], allPortals)

    def server_agents(self, include=None, allPortals=False):
        return devices.servers(self, include if include else [], allPortals)

    def desktop_agents(self, include=None, allPortals=False):
        return devices.desktops(self, include if include else [], allPortals)

    def devices_by_name(self, names, include=None):
        return devices.by_name(self, include if include else [], names)

    def devices(self, include=None, allPortals=False, filters=None):
        return devices.devices(self, include if include else [], allPortals, filters if filters else [])

    def generate_code(self, username, tenant=None):
        return activation.generate_code(self, username, tenant)

    def cloudfs(self):
        return cloudfs.CloudFS(self)

    def zones(self):
        return zones.Zones(self)

    def files(self):
        return files.FileBrowser(self)

    def logs(self, topic=enum.LogTopic.System, minSeverity=enum.Severity.INFO, originType=enum.OriginType.Portal, before=None, after=None):
        return logs.logs(self, topic, minSeverity, originType, before, after)

    def _api(self):
        return self._baseurl() + '/api'

    def _baseurl(self):
        raise NotImplementedError("Subclass must implement the _baseurl method")


class GlobalAdmin(Portal):

    def __init__(self, host, port=443, https=True):
        super().__init__(host, port, https)

    def browse_tenant(self, tenant_name):
        portals.browse(self, tenant_name)

    def browse_global_admin(self):
        self.browse_tenant('')

    def servers(self, include=None):
        return servers.servers(self, include if include else [])

    def tenants(self, include_deleted=False):
        return portals.portals(self, include_deleted)

    def add_tenant(self, name, display_name=None, billing_id=None, company=None):
        return portals.add(self, name, display_name, billing_id, company)

    def delete_tenant(self, name):
        return portals.delete(self, name)

    def undelete_tenant(self, name):
        return portals.undelete(self, name)

    @staticmethod
    def _files():
        return '/admin/webdav/Users'

    def _baseurl(self):
        return NetworkHost.baseurl(self) + '/' + self._context()

    @staticmethod
    def _context():
        return 'admin'


class ServicesPortal(Portal):

    def __init__(self, host, port=443, https=True):
        super().__init__(host, port, https)

    @staticmethod
    def _files():
        return '/ServicesPortal/webdav'

    def _baseurl(self):
        return NetworkHost.baseurl(self) + '/' + self._context()

    @staticmethod
    def _context():
        return 'ServicesPortal'
