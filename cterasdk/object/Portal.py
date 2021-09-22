from ..client import CTERAHost, authenticated
from ..core import connection
from ..core import activation
from ..core import antivirus
from ..core import buckets
from ..core import decorator
from ..core import directoryservice
from ..core import firmwares
from ..core import login
from ..core import query
from ..core import logs
from ..core import portals
from ..core import plans
from ..core import reports
from ..core import servers
from ..core import devices
from ..core import session
from ..core import users
from ..core import cloudfs
from ..core import zones
from ..core import settings
from ..core import setup
from ..core import ssl
from ..core import startup
from ..core import syslog
from ..core import taskmgr
from ..core import templates
from ..core import uri
from ..core import files


class Portal(CTERAHost):  # pylint: disable=too-many-instance-attributes
    """
    Parent class for communicating with the Portal through either GlobalAdmin or ServicesPortal

    :ivar cterasdk.core.users.Users users: Object holding the Portal user APIs
    :ivar cterasdk.core.plans.Plans plans: Object holding the Plan APIs
    :ivar cterasdk.core.reports.Reports reports: Object holding the Portal reports APIs
    :ivar cterasdk.core.devices.Devices devices: Object holding the Portal devices APIs
    :ivar cterasdk.core.directoryservice.DirectoryService directoryservice: Object holding the Portal Active Directory Service APIs
    :ivar cterasdk.core.zones.Zones zones: Object holding the Portal zones APIs
    :ivar cterasdk.core.activation.Activation activation: Object holding the Portal activation APIs
    :ivar cterasdk.core.logs.Logs logs: Object holding the Portal logs APIs
    :ivar cterasdk.core.cloudfs.CloudFS cloudfs: Object holding the Portal CloudFS APIs
    :ivar cterasdk.core.settings.Settings settings: Object holding the Portal Settings APIs
    :ivar cterasdk.core.taskmgr.Tasks tasks: Object holding the Portal Background Tasks APIs
    :ivar cterasdk.core.templates.Templates templates: Object holding the Portal Configuration Templates APIs
    :ivar cterasdk.core.firmwares.Firmwares firmwares: Object holding the Portal Firmware Repository APIs
    :ivar cterasdk.core.files.browser.FileBrowser files: Object holding the Portal File Browsing APIs
    """

    def __init__(self, host, port, https):
        """
        :param str host: The fully qualified domain name, hostname or an IPv4 address of the Gateway
        :param int port: Set a custom port number (0 - 65535)
        :param bool https: Set to True to require HTTPS
        """
        super().__init__(host, port, https)
        self._session = session.Session(self.host(), self.context)
        self.users = users.Users(self)
        self.reports = reports.Reports(self)
        self.plans = plans.Plans(self)
        self.devices = devices.Devices(self)
        self.directoryservice = directoryservice.DirectoryService(self)
        self.zones = zones.Zones(self)
        self.cloudfs = cloudfs.CloudFS(self)
        self.activation = activation.Activation(self)
        self.files = files.CloudDrive(self, self.cloud_drive_base_path)
        self.backups = files.Backups(self, self.backups_base_path)
        self.logs = logs.Logs(self)
        self.settings = settings.Settings(self)
        self.tasks = taskmgr.Tasks(self)
        self.templates = templates.Templates(self)
        self.firmwares = firmwares.Firmwares(self)

    @property
    def base_api_url(self):
        return uri.api(self)

    @property
    def base_portal_url(self):
        return self.baseurl() + '/' + self.context

    @property
    def base_file_url(self):
        return self.baseurl()

    @property
    def _session_id_key(self):
        return 'JSESSIONID'

    @property
    def context(self):
        raise NotImplementedError("Implementing class must implement the context property")

    @property
    def cloud_drive_base_path(self):
        raise NotImplementedError("Implementing class must implement the cloud_drive_base_path property")

    @property
    def backups_base_path(self):
        raise NotImplementedError("Implementing class must implement the backups_base_path property")

    @property
    def _omit_fields(self):
        return super()._omit_fields + [
            'users',
            'reports',
            'plans',
            'devices',
            'directoryservice',
            'zones',
            'cloudfs',
            'activation',
            'files',
            'logs',
            'settings',
            'tasks',
            'templates',
            'firmwares'
        ]

    @property
    def _login_object(self):
        return login.Login(self)

    def _is_authenticated(self, function, *args, **kwargs):
        def is_public(path):
            return path.startswith(f'/{self.context}/public')

        def is_setup(path):
            return path.startswith(f'/{self.context}/setup')

        def is_startup(path):
            return path.startswith(f'/{self.context}/startup')
        current_session = self.session()
        return current_session.authenticated() or current_session.initializing() or \
            is_public(args[0]) or is_setup(args[0]) or is_startup(args[0]) or \
            current_session.is_local_auth()

    def test(self):
        """ Verification check to ensure the target host is a Portal. """
        connection.test(self)
        return self.public_info()

    def public_info(self):
        """ Obtain the Portal's public info. """
        return self.get('/' + self.context + '/public/publicInfo', params={}, use_file_url=True)

    @decorator.update_current_tenant
    def put(self, path, value, use_file_url=False):
        return super().put(path, value, use_file_url=use_file_url)

    @authenticated
    def query(self, path, param):
        return query.query(self, path, param)

    @authenticated
    def show_query(self, path, param):
        return query.show(self, path, param)

    def iterator(self, path, param):
        return query.iterator(self, path, param)


class GlobalAdmin(Portal):
    """
    Main class for Global Admin operations on a Portal

    :ivar cterasdk.core.portals.Portals portals: Object holding the Portals Management APIs
    :ivar cterasdk.core.servers.Servers servers: Object holding the Servers Management APIs
    :ivar cterasdk.core.setup.Setup setup: Object holding the Portal setup APIs
    :ivar cterasdk.core.ssl.SSL ssl: Object holding the Portal SSL Certificate APIs
    :ivar cterasdk.core.startup.Startup startup: Object holding the Portal startup APIs
    :ivar cterasdk.core.syslog.Syslog syslog: Object holding the Portal syslog APIs
    :ivar cterasdk.core.antivirus.Antivirus antivirus: Object holding the Portal Antivirus APIs
    :ivar cterasdk.core.buckets.Buckets buckets: Object holding the Portal Storage Node APIs
    """

    def __init__(self, host, port=None, https=True):
        """
        :param str host: The fully qualified domain name, hostname or an IPv4 address of the Portal
        :param int,optional port: Set a custom port number (0 - 65535), If not set defaults to 80 for http and 443 for https
        :param bool,optional https: Set to True to require HTTPS, defaults to True
        """
        super().__init__(host, port, https)
        self.portals = portals.Portals(self)
        self.servers = servers.Servers(self)
        self.setup = setup.Setup(self)
        self.ssl = ssl.SSL(self)
        self.startup = startup.Startup(self)
        self.syslog = syslog.Syslog(self)
        self.antivirus = antivirus.Antivirus(self)
        self.buckets = buckets.Buckets(self)

    @property
    def _omit_fields(self):
        return super()._omit_fields + ['portals', 'servers', 'setup', 'ssl', 'startup', 'syslog', 'antivirus', 'buckets']

    @property
    def context(self):
        return 'admin'

    @property
    def cloud_drive_base_path(self):
        return '/admin/webdav/Users'

    @property
    def backups_base_path(self):
        return '/admin/webdav/backupFolders'


class ServicesPortal(Portal):
    """
    Main class for Service operations on a Portal
    """

    def __init__(self, host, port=None, https=True):
        """
        :param str host: The fully qualified domain name, hostname or an IPv4 address of the Portal
        :param int,optional port: Set a custom port number (0 - 65535), If not set defaults to 80 for http and 443 for https
        :param bool,optional https: Set to True to require HTTPS, defaults to True
        """
        super().__init__(host, port, https)

    @property
    def context(self):
        return 'ServicesPortal'

    @property
    def cloud_drive_base_path(self):
        return '/ServicesPortal/webdav'

    @property
    def backups_base_path(self):
        return '/ServicesPortal/webdav/backups'
