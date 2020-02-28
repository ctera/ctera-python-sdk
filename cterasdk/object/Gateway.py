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


class Gateway(CTERAHost):  # pylint: disable=too-many-instance-attributes

    def __init__(self, host, port=80, https=False, Portal=None):
        super().__init__(host, port, https)
        self._remote_access = False
        if Portal is not None:
            self._Portal = Portal
            self._ctera_client = Portal._ctera_client
            session.start_remote_session(self, Portal)
        else:
            session.inactive_session(self)
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

    @property
    def base_api_url(self):
        return uri.api(self)

    @property
    def base_file_url(self):
        return uri.files(self)

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
            'files'
            ]

    @property
    def _login_object(self):
        return login.Login(self)

    def _is_authenticated(self, function, *args, **kwargs):
        def is_nosession(path):
            return function.__name__ == 'get' and path.startswith('/nosession')
        current_session = self.session()
        return current_session.authenticated() or is_nosession(args[0])

    def test(self):
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
