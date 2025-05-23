from abc import abstractmethod
import cterasdk.settings
from ...clients import clients
from ..services import Management
from ..endpoints import EndpointBuilder
from .. import authenticators
from ...lib.session.core import Session
from ...core import (
    activation, admins, antivirus, buckets, cli, cloudfs, connection, credentials,
    devices, directoryservice, domains, files, firmwares, groups, kms, licenses,
    login, logs, mail, messaging, plans, portals, reports, roles, servers, settings,
    setup, ssl, startup, storage_classes, syslog, taskmgr, templates, users,
)


class Clients:

    def __init__(self, core):
        self.ctera = core.default.clone(clients.Extended, EndpointBuilder.new(core.base, core.context))
        self.api = core.default.clone(clients.API, EndpointBuilder.new(core.base, core.context, '/api'))
        self.io = IO(core)


class IO:

    def __init__(self, core):
        self._folders = core.default.clone(clients.Folders, EndpointBuilder.new(core.base, core.context, '/folders/folders'))
        self._upload = core.default.clone(clients.Upload, EndpointBuilder.new(core.base, core.context, '/upload/folders'))
        self._webdav = core.default.clone(clients.WebDAV, EndpointBuilder.new(core.base, core.context, '/webdav'))

    @property
    def upload(self):
        return self._upload.upload

    @property
    def download(self):
        return self._webdav.download

    @property
    def download_zip(self):
        return self._folders.download_zip

    @property
    def builder(self):
        return self._webdav._builder  # pylint: disable=protected-access


class Portal(Management):  # pylint: disable=too-many-instance-attributes

    def __init__(self, host, port=None, https=True):
        super().__init__(host, port, https, None, cterasdk.settings.core.syn.settings)
        self._ctera_session = Session(self.host(), self.context)
        self._ctera_clients = Clients(self)
        self.activation = activation.Activation(self)
        self.admins = admins.Administrators(self)
        self.backups = files.Backups(self)
        self.cloudfs = cloudfs.CloudFS(self)
        self.credentials = credentials.Credentials(self)
        self.devices = devices.Devices(self)
        self.directoryservice = directoryservice.DirectoryService(self)
        self.domains = domains.Domains(self)
        self.files = files.CloudDrive(self)
        self.firmwares = firmwares.Firmwares(self)
        self.groups = groups.Groups(self)
        self.logs = logs.Logs(self)
        self.plans = plans.Plans(self)
        self.reports = reports.Reports(self)
        self.roles = roles.Roles(self)
        self.settings = settings.Settings(self)
        self.storage_classes = storage_classes.StorageClasses(self)
        self.tasks = taskmgr.Tasks(self)
        self.templates = templates.Templates(self)
        self.users = users.Users(self)

    @property
    def ctera(self):
        return self.clients.ctera

    @property
    def api(self):
        return self.clients.api

    @property
    def io(self):
        return self.clients.io

    @property
    @abstractmethod
    def context(self):
        return NotImplementedError("Subclass must implement the 'context' property")

    @property
    def _session_id_key(self):
        return 'JSESSIONID'

    def _authenticator(self, url):
        return authenticators.core(self.session(), url, self.context)

    @property
    def _login_object(self):
        return login.Login(self)

    def test(self):
        return connection.test(self)

    def public_info(self):
        return self.ctera.get('/public/publicInfo')

    @property
    def _omit_fields(self):
        return super()._omit_fields + ['activation', 'admins', 'cloudfs', 'credentials', 'devices', 'directoryservice', 'domains', 'files',
                                       'firmwares', 'groups', 'logs', 'plans', 'reports', 'roles', 'settings', 'tasks', 'templates',
                                       'users']


class GlobalAdmin(Portal):  # pylint: disable=too-many-instance-attributes

    def __init__(self, host, port=None, https=True):
        super().__init__(host, port, https)
        self.antivirus = antivirus.Antivirus(self)
        self.buckets = buckets.Buckets(self)
        self.cli = cli.CLI(self)
        self.kms = kms.KMS(self)
        self.licenses = licenses.Licenses(self)
        self.mail = mail.Mail(self)
        self.messaging = messaging.Messaging(self)
        self.portals = portals.Portals(self)
        self.servers = servers.Servers(self)
        self.setup = setup.Setup(self)
        self.ssl = ssl.SSL(self)
        self.startup = startup.Startup(self)
        self.syslog = syslog.Syslog(self)

    @property
    def context(self):
        return 'admin'

    def impersonate(self, username, tenant):
        """
        Impersonate a Portal user

        :param str username: Username
        :param str tenant: Tenant
        """
        ctera_ticket = self.users.generate_ticket(username, tenant)
        user = ServicesPortal(f'{tenant}.{self.settings.global_settings.dns_suffix}', self.port())
        user.sso(ctera_ticket)
        return user

    @property
    def _omit_fields(self):
        return super()._omit_fields + ['antivirus', 'buckets', 'cli', 'kms', 'licenses', 'mail', 'messaging', 'portals', 'servers',
                                       'setup', 'ssl', 'startup', 'syslog']


class ServicesPortal(Portal):

    @property
    def context(self):
        return 'ServicesPortal'

    def sso(self, ctera_ticket):
        """
        Login using a Portal ticket

        :param str ctera_ticket: SSO Ticket.
        """
        self._login_object.sso(ctera_ticket)
        self.session().start_session(self)
        self.api.web_session()
