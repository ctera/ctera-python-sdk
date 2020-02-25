import urllib.parse

from ..client import CTERAHost, authenticated
from ..core import connection
from ..core import activation
from ..core import directoryservice
from ..core import login
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


class Portal(CTERAHost):

    def __init__(self, host, port, https):
        super().__init__(host, port, https)
        session.inactive_session(self)
        self.login = login.Login(self)
        self.users = users.Users(self)
        self.devices = devices.Devices(self)
        self.directoryservice = directoryservice.DirectoryService(self)
        self.zones = zones.Zones(self)
        self.cloudfs = cloudfs.CloudFS(self)
        self.activation = activation.Activation(self)
        self.files = files.FileBrowser(self, self.file_browser_base_path)
        self.logs = logs.Logs(self)

    @property
    def base_api_url(self):
        raise NotImplementedError("Implementing class must implement the base_api_url property")

    @property
    def context(self):
        raise NotImplementedError("Implementing class must implement the context property")

    @property
    def file_browser_base_path(self):
        raise NotImplementedError("Implementing class must implement the file_browser_base_path property")

    @property
    def _omit_fields(self):
        return super()._omit_fields + [
            'login',
            'users',
            'devices',
            'directoryservice',
            'zones',
            'cloudfs',
            'activation',
            'files',
            'logs',
        ]

    def _is_authenticated(self, function, *args, **kwargs):
        current_session = self.session()
        return current_session.authenticated() or current_session.initializing()

    def test(self):
        connection.test(self)
        return self.get('/public/publicInfo', params={})

    @authenticated
    def query(self, path, param):
        return query.query(self, path, param)

    @authenticated
    def show_query(self, path, param):
        return query.show(self, path, param)

    def iterator(self, path, param):
        return query.iterator(self, path, param)


class GlobalAdmin(Portal):

    def __init__(self, host, port=443, https=True):
        super().__init__(host, port, https)
        self.portals = portals.Portals(self)
        self.servers = servers.Servers(self)
        self._base_api_url = None
        self._base_file_url = None

    @property
    def base_api_url(self):
        if self._base_api_url is None:
            self._base_api_url = urllib.parse.urljoin(self.baseurl(), 'admin/api')
        return self._base_api_url

    @property
    def base_file_url(self):
        if self._base_file_url is None:
            pass
        return self._base_file_url

    @property
    def _omit_fields(self):
        return super()._omit_fields + ['portals', 'servers']

    @property
    def context(self):
        return 'admin'

    @property
    def file_browser_base_path(self):
        return '/admin/webdav/Users'


class ServicesPortal(Portal):

    def __init__(self, host, port=443, https=True):
        super().__init__(host, port, https)
        self._base_api_url = None
        self._base_file_url = None

    @property
    def base_api_url(self):
        if self._base_api_url is None:
            self._base_api_url = urllib.parse.urljoin(self.baseurl(), 'ServicesPortal/api')
        return self._base_api_url

    @property
    def base_file_url(self):
        if self._base_file_url is None:
            pass
        return self._base_file_url

    @property
    def context(self):
        return 'ServicesPortal'

    @property
    def file_browser_base_path(self):
        return '/ServicesPortal/webdav'
