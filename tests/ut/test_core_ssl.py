import munch
from cterasdk.core import ssl
from tests.ut import base_core


class TestCoreSSL(base_core.BaseCoreTest):

    def test_get_certificate(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = ssl.SSL(self._global_admin).get()
        self._global_admin.api.get.assert_called_once_with('/settings/ca')
        self.assertEqual(ret, get_response)

    def test_thumbprint(self):
        thumbprint = 'thumbprint'
        get_response = munch.Munch({'thumbprint': thumbprint})
        self._init_global_admin(get_response=get_response)
        ret = ssl.SSL(self._global_admin).thumbprint
        self._global_admin.api.get.assert_called_once_with('/settings/ca')
        self.assertEqual(ret, thumbprint)
