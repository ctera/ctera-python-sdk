from ..client import NetworkHost, CTERAHost
from ..edge import backup
from ..edge import cli
from ..edge import logs
from ..edge import services
from ..edge import session
from ..edge import support
from ..edge import sync
from ..edge import uri


class Agent(CTERAHost):
    """
    Main class operating on a Agent

    :ivar cterasdk.edge.backup.Backup backup: Object holding the Agent Backup APIs
    :ivar cterasdk.edge.cli.CLI cli: Object holding the Agent CLI APIs
    :ivar cterasdk.edge.logs.Logs logs: Object holding the Agent Logs APIs
    :ivar cterasdk.edge.services.Services services: Object holding the Agent Services APIs
    :ivar cterasdk.edge.support.Support support: Object holding the Agent Support APIs
    :ivar cterasdk.edge.sync.Sync sync: Object holding the Agent Sync APIs
    """

    def __init__(self, host, port=80, https=False, Portal=None):
        """
        :param str host: The fully qualified domain name, hostname or an IPv4 address of the Gateway
        :param int,optional port: Set a custom port number (0 - 65535), defaults to 80
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
        self.backup = backup.Backup(self)
        self.cli = cli.CLI(self)
        self.logs = logs.Logs(self)
        self.services = services.Services(self)
        self.support = support.Support(self)
        self.sync = sync.Sync(self)

    @property
    def base_api_url(self):
        return uri.api(self)

    @property
    def _login_object(self):
        raise NotImplementedError("Currently login is not supported for Agent")

    @property
    def _session_id_key(self):
        return ''

    @property
    def _omit_fields(self):
        return super()._omit_fields + [
            'backup',
            'cli',
            'logs',
            'services',
            'support',
            'sync'
        ]

    def _is_authenticated(self, function, *args, **kwargs):
        return True

    def _api(self):
        return uri.api(self)

    def _baseurl(self):
        return NetworkHost.baseurl(self)
