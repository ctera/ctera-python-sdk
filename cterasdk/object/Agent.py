from ..client import NetworkHost, CTERAHost


class Agent(CTERAHost):

    def __init__(self, host, port=80, https=False, Portal=None):
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

    def _is_authenticated(self, function, *args, **kwargs):
        return True

    def test(self):
        '''
        {
            "desc": "Verify the target host is a CTERA Gateway"
        }
        '''
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
