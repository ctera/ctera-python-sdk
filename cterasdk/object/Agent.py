from ..client import NetworkHost, CTERAHost


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
        self._Portal = Portal
        if self._Portal is not None:
            self._ctera_client = Portal._ctera_client

    @property
    def base_api_url(self):
        return self._api()

    @property
    def base_file_url(self):
        return self._api()

    @property
    def _login_object(self):
        raise NotImplementedError("Currently login is not supported for Agent")

    def _is_authenticated(self, function, *args, **kwargs):
        return True

    def test(self):
        """ Test connectivity """
        NetworkHost.test_conn(self)
        self.get('/nosession/logininfo')

    def _api(self):
        if self._remote_access:
            return self._Portal.baseurl + '/devices/' + self._Portal.device_name + '/admingui/api'

        if self._Portal is not None:
            return self._Portal.baseurl + '/devicecmdnew/' + self._Portal.tenant_name + '/' + self._Portal.device_name + '/'

        return self._baseurl() + '/admingui/api'

    def _baseurl(self):
        return self.baseurl()
