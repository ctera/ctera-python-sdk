from ..client import NetworkHost, CTERAHost
from ..edge import session
from ..edge import uri


class Agent(CTERAHost):
    """
    Main class operating on a Agent
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

    @property
    def base_api_url(self):
        return uri.api(self)

    @property
    def _login_object(self):
        raise NotImplementedError("Currently login is not supported for Agent")

    @property
    def _session_id_key(self):
        return ''

    def _is_authenticated(self, function, *args, **kwargs):
        return True

    def _api(self):
        return uri.api(self)

    def _baseurl(self):
        return NetworkHost.baseurl(self)
