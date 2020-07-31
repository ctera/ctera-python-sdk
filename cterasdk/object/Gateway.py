from ..client import NetworkHost, CTERAHost
from ..edge import decorator
from ..edge import connection
from ..edge import query
from ..edge import afp
from ..edge import aio
from ..edge import array
from ..edge import audit
from ..edge import backup
from ..edge import cache
from ..edge import cli
from ..edge import config
from ..edge import directoryservice
from ..edge import drive
from ..edge import ftp
from ..edge import groups
from ..edge import licenses
from ..edge import login
from ..edge import logs
from ..edge import mail
from ..edge import network
from ..edge import nfs
from ..edge import ntp
from ..edge import ssl
from ..edge import power
from ..edge import rsync
from ..edge import services
from ..edge import session
from ..edge import shares
from ..edge import shell
from ..edge import smb
from ..edge import support
from ..edge import sync
from ..edge import syslog
from ..edge import telnet
from ..edge import timezone
from ..edge import users
from ..edge import volumes
from ..edge import files
from ..edge import remote
from ..edge import uri
from ..edge import firmware


class Gateway(CTERAHost):  # pylint: disable=too-many-instance-attributes
    """
    Main class operating on a Gateway

    :ivar cterasdk.edge.config.Config config: Object holding the Gateway Configuration APIs
    :ivar cterasdk.edge.network.Network network: Object holding the Gateway Network APIs
    :ivar cterasdk.edge.licenses.Licenses licenses: Object holding the Gateway Licenses APIs
    :ivar cterasdk.edge.services.Services services: Object holding the Gateway Services APIs
    :ivar cterasdk.edge.directoryservice.DirectoryService directoryservice: Object holding the Gateway Active Directory APIs
    :ivar cterasdk.edge.telnet.Telnet telnet: Object holding the Gateway Telnet APIs
    :ivar cterasdk.edge.syslog.Syslog syslog: Object holding the Gateway Syslog APIs
    :ivar cterasdk.edge.audit.Audit audit: Object holding the Gateway Audit APIs
    :ivar cterasdk.edge.mail.Mail mail: Object holding the Gateway Mail APIs
    :ivar cterasdk.edge.backup.Backup backup: Object holding the Gateway Backup APIs
    :ivar cterasdk.edge.sync.Sync sync: Object holding the Gateway Sync APIs
    :ivar cterasdk.edge.cache.Cache cache: Object holding the Gateway Cache APIs
    :ivar cterasdk.edge.ssl.SSL ssl: Object holding the Gateway SSL APIs
    :ivar cterasdk.edge.power.Power power: Object holding the Gateway Power APIs
    :ivar cterasdk.edge.users.Users users: Object holding the Gateway Users APIs
    :ivar cterasdk.edge.groups.Groups groups: Object holding the Gateway Groups APIs
    :ivar cterasdk.edge.drive.Drive drive: Object holding the Gateway Drive APIs
    :ivar cterasdk.edge.volumes.Volumes volumes: Object holding the Gateway Volumes APIs
    :ivar cterasdk.edge.array.Array array: Object holding the Gateway Array APIs
    :ivar cterasdk.edge.shares.Shares shares: Object holding the Gateway Shares APIs
    :ivar cterasdk.edge.smb.SMB smb: Object holding the Gateway SMB APIs
    :ivar cterasdk.edge.aio.AIO aio: Object holding the Gateway AIO APIs
    :ivar cterasdk.edge.ftp.FTP ftp: Object holding the Gateway FTP APIs
    :ivar cterasdk.edge.afp.AFP afp: Object holding the Gateway AFP APIs
    :ivar cterasdk.edge.nfs.NFS nfs: Object holding the Gateway NFS APIs
    :ivar cterasdk.edge.rsync.RSync rsync: Object holding the Gateway RSync APIs
    :ivar cterasdk.edge.timezone.Timezone timezone: Object holding the Gateway Timezone APIs
    :ivar cterasdk.edge.logs.Logs logs: Object holding the Gateway Logs APIs
    :ivar cterasdk.edge.ntp.NTP ntp: Object holding the Gateway NTP APIs
    :ivar cterasdk.edge.shell.Shell shell: Object holding the Gateway Shell APIs
    :ivar cterasdk.edge.cli.CLI cli: Object holding the Gateway CLI APIs
    :ivar cterasdk.edge.support.Support support: Object holding the Gateway Support APIs
    :ivar cterasdk.edge.files.FileBrowser files: Object holding the Gateway File Browsing APIs
    :ivar cterasdk.edge.firmware.Fireware firmware: Object holding the Gateway Firmware APIs
    """

    def __init__(self, host, port=None, https=False, Portal=None):
        """
        :param str host: The fully qualified domain name, hostname or an IPv4 address of the Gateway
        :param int,optional port: Set a custom port number (0 - 65535), If not set defaults to 80 for http and 443 for https
        :param bool,optional https: Set to True to require HTTPS, defaults to False
        :param cterasdk.object.Portal.Portal,optional Portal: The portal throught which the remote session was created, defaults to None
        """
        super().__init__(host, port, https)
        self._remote_access = False
        self._session = session.Session(self.host())
        if Portal is not None:
            self._Portal = Portal
            self._ctera_client = Portal._ctera_client
            self._session.start_remote_session(self._Portal.session())
        self.config = config.Config(self)
        self.network = network.Network(self)
        self.licenses = licenses.Licenses(self)
        self.services = services.Services(self)
        self.directoryservice = directoryservice.DirectoryService(self)
        self.telnet = telnet.Telnet(self)
        self.syslog = syslog.Syslog(self)
        self.audit = audit.Audit(self)
        self.mail = mail.Mail(self)
        self.backup = backup.Backup(self)
        self.sync = sync.Sync(self)
        self.cache = cache.Cache(self)
        self.ssl = ssl.SSL(self)
        self.power = power.Power(self)
        self.users = users.Users(self)
        self.groups = groups.Groups(self)
        self.drive = drive.Drive(self)
        self.volumes = volumes.Volumes(self)
        self.array = array.Array(self)
        self.shares = shares.Shares(self)
        self.smb = smb.SMB(self)
        self.aio = aio.AIO(self)
        self.ftp = ftp.FTP(self)
        self.afp = afp.AFP(self)
        self.nfs = nfs.NFS(self)
        self.rsync = rsync.RSync(self)
        self.timezone = timezone.Timezone(self)
        self.logs = logs.Logs(self)
        self.ntp = ntp.NTP(self)
        self.shell = shell.Shell(self)
        self.cli = cli.CLI(self)
        self.support = support.Support(self)
        self.files = files.FileBrowser(self)
        self.firmware = firmware.Firmware(self)

    @property
    def base_api_url(self):
        return uri.api(self)

    @property
    def base_file_url(self):
        return uri.files(self)

    @property
    def _session_id_key(self):
        return '_cteraSessionId_'

    @staticmethod
    def make_local_files_dir(full_path):
        return 'localFiles/%s' % full_path

    @property
    def _omit_fields(self):
        return super()._omit_fields + [
            'config',
            'network',
            'licenses',
            'services',
            'directoryservice',
            'telnet',
            'syslog',
            'audit',
            'mail',
            'backup',
            'sync',
            'cache',
            'ssl',
            'power',
            'users',
            'groups',
            'drive',
            'volumes',
            'array',
            'shares',
            'smb',
            'aio',
            'ftp',
            'afp',
            'nfs',
            'rsync',
            'timezone',
            'logs',
            'ntp',
            'shell',
            'cli',
            'support',
            'files',
            'firmware'
            ]

    @property
    def _login_object(self):
        return login.Login(self)

    def _is_authenticated(self, function, *args, **kwargs):
        def is_nosession(path):
            return path.startswith('/nosession')
        current_session = self.session()
        return current_session.authenticated() or current_session.initializing or is_nosession(args[0])

    def test(self):
        """ Verification check to ensure the target host is a Gateway. """
        return connection.test(self)

    def remote_access(self):
        remote.remote_access(self, self._Portal)

    @decorator.authenticated
    def query(self, path, key, value):
        return query.query(self, path, key, value)

    @decorator.authenticated
    def show_query(self, path, key, value):
        query.show(self, path, key, value)

    @decorator.authenticated
    def rm(self, path):
        return super().delete(path, use_file_url=True)

    def _api(self):
        return uri.api(self)

    def _files(self):
        return uri.files(self)

    def _baseurl(self):
        return NetworkHost.baseurl(self)
