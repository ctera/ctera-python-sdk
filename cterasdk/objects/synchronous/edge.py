import cterasdk.settings
from ...clients import clients
from ..services import Management
from ..endpoints import EndpointBuilder
from .. import authenticators
from ...lib.session.edge import Session

from ...edge import (
    afp, aio, array, audit, backup, cache, cli, config, connection, ctera_migrate,
    dedup, directoryservice, drive, files, firmware, ftp, groups, licenses, login,
    logs, mail, network, nfs, ntp, power, remote, rsync, ransom_protect, services,
    shares, shell, smb, snmp, ssh, ssl, support, sync, syslog, taskmgr, telnet,
    timezone, users, volumes,
)


class Clients:

    def __init__(self, edge, Portal):
        if Portal:
            edge._Portal = Portal
            edge.default.close()
            edge._ctera_session.start_remote_session(Portal.session())
            self.api = Portal.default.clone(clients.API, EndpointBuilder.new(edge.base), authenticator=lambda *_: True)
        else:
            self.migrate = edge.default.clone(clients.Migrate, EndpointBuilder.new(edge.base, '/migration/rest/v1'))
            self.api = edge.default.clone(clients.API, EndpointBuilder.new(edge.base, '/admingui/api'))
            self.io = IO(edge)


class IO:

    def __init__(self, edge):
        self._edge = edge
        self._webdav = edge.default.clone(clients.WebDAV, EndpointBuilder.new(edge.base, '/localFiles'))

    @property
    def download(self):
        return self._webdav.download

    @property
    def download_zip(self):
        return self._edge.default.form_data  # pylint: disable=protected-access

    @property
    def upload(self):
        return self._edge.default.form_data  # pylint: disable=protected-access

    @property
    def propfind(self):
        return self._webdav.propfind

    @property
    def mkdir(self):
        return self._webdav.mkcol

    @property
    def copy(self):
        return self._webdav.copy

    @property
    def move(self):
        return self._webdav.move

    @property
    def delete(self):
        return self._webdav.delete


class Edge(Management):  # pylint: disable=too-many-instance-attributes

    def __init__(self, host=None, port=None, https=True, Portal=None, *, base=None):
        super().__init__(host, port, https, base, cterasdk.settings.edge.syn.settings)
        self._ctera_session = Session(self.host())
        self._ctera_clients = Clients(self, Portal)
        self.afp = afp.AFP(self)
        self.aio = aio.AIO(self)
        self.array = array.Array(self)
        self.audit = audit.Audit(self)
        self.backup = backup.Backup(self)
        self.cache = cache.Cache(self)
        self.cli = cli.CLI(self)
        self.config = config.Config(self)
        self.ctera_migrate = ctera_migrate.CTERAMigrate(self)
        self.dedup = dedup.Dedup(self)
        self.directoryservice = directoryservice.DirectoryService(self)
        self.drive = drive.Drive(self)
        self.files = files.FileBrowser(self)
        self.firmware = firmware.Firmware(self)
        self.ftp = ftp.FTP(self)
        self.groups = groups.Groups(self)
        self.licenses = licenses.Licenses(self)
        self.logs = logs.Logs(self)
        self.mail = mail.Mail(self)
        self.network = network.Network(self)
        self.nfs = nfs.NFS(self)
        self.ntp = ntp.NTP(self)
        self.power = power.Power(self)
        self.ransom_protect = ransom_protect.RansomProtect(self)
        self.rsync = rsync.RSync(self)
        self.services = services.Services(self)
        self.shares = shares.Shares(self)
        self.shell = shell.Shell(self)
        self.smb = smb.SMB(self)
        self.snmp = snmp.SNMP(self)
        self.ssh = ssh.SSH(self)
        self.ssl = ssl.SSL(self)
        self.support = support.Support(self)
        self.sync = sync.Sync(self)
        self.syslog = syslog.Syslog(self)
        self.tasks = taskmgr.Tasks(self)
        self.telnet = telnet.Telnet(self)
        self.timezone = timezone.Timezone(self)
        self.users = users.Users(self)
        self.volumes = volumes.Volumes(self)

    def _after_login(self):
        self.ssl = ssl.initialize(self)

    @property
    def migrate(self):
        return self.clients.migrate

    @property
    def api(self):
        return self.clients.api

    @property
    def io(self):
        return self.clients.io

    @property
    def _session_id_key(self):
        return '_cteraSessionId_'

    def _authenticator(self, url):
        return authenticators.edge(self.session(), url)

    @property
    def _login_object(self):
        return login.Login(self)

    @property
    def initialized(self):
        return not self._login_object.info().isfirstlogin

    def test(self):
        return connection.test(self)

    def sso(self, ticket):
        """ Login using Single Sign On"""
        self._login_object.sso(ticket)
        self.session().start_session(self)

    def remote_access(self):
        return remote.remote_access(self, self._Portal)

    @property
    def _omit_fields(self):
        return super()._omit_fields + ['afp', 'aio', 'array', 'audit', 'backup', 'cache', 'cli', 'config', 'ctera_migrate', 'dedup',
                                       'directoryservice', 'drive', 'files', 'firmware', 'ftp', 'groups', 'licenses', 'logs', 'mail',
                                       'network', 'nfs', 'ntp', 'power', 'ransom_protect', 'rsync', 'services', 'shares', 'shell',
                                       'smb', 'snmp', 'ssh', 'ssl', 'support', 'sync', 'syslog', 'tasks', 'telnet', 'timezone',
                                       'users', 'volumes']
