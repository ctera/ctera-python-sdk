from ..client import NetworkHost, CTERAHost


class Agent(CTERAHost):

    def __init__(self, host, port=80, https=False, Portal=None):
        super().__init__(host, port, https)
        self._remote_access = False
        if Portal is not None:
            self._Portal = Portal
            self._ctera_client = Portal._ctera_client

    def test(self):
        '''
        {
            "desc": "Verify the target host is a CTERA Gateway"
        }
        '''
        NetworkHost.test_conn(self)
        self.get('/nosession/logininfo')

    def get(self, path, params=None):
        return CTERAHost.get(self, self._api(), path, params if params else {})

    def show(self, path):
        CTERAHost.show(self, self._api(), path)

    def get_multi(self, paths):
        return CTERAHost.get_multi(self, self._api(), paths)

    def show_multi(self, paths):
        CTERAHost.show_multi(self, self._api(), paths)

    def put(self, path, value):
        return CTERAHost.put(self, self._api(), path, value)

    def post(self, path, value):
        return CTERAHost.post(self, self._api(), path, value)

    def execute(self, path, name, param=None):
        return CTERAHost.execute(self, self._api(), path, name, param)

    def add(self, path, param):
        return CTERAHost.add(self, self._api(), path, param)

    def delete(self, path):
        return CTERAHost.delete(self, self._api(), path)

    def _api(self):
        if self._remote_access:
            return self._Portal.baseurl + '/devices/' + self._Portal.device_name + '/admingui/api'

        if hasattr(self, '_Portal') and self._Portal is not None:
            return self._Portal.baseurl + '/devicecmdnew/' + self._Portal.tenant_name + '/' + self._Portal.device_name + '/'

        return self._baseurl() + '/admingui/api'

    def _baseurl(self):
        return NetworkHost.baseurl(self)
