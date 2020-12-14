from unittest import mock

from cterasdk.edge import ssl
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeSSL(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._private_key = './certs/private.key'
        self._domain_cert = './certs/certificate.crt'
        self._intermediate = './certs/intermediate.crt'
        self._ca = './certs/ca.crt'
        self._certificate = ssl.SSL.BEGIN_PEM

    def test_is_http_disabled_true(self):
        get_response = True
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_http_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, get_response)

    def test_is_http_disabled_false(self):
        get_response = False
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_http_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, get_response)

    def test_is_http_enabled_true(self):
        get_response = False
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_http_enabled()
        self._filer.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, True)

    def test_is_http_enabled_false(self):
        get_response = True
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_http_enabled()
        self._filer.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, False)

    def test_enable_http(self):
        self._init_filer()
        ssl.SSL(self._filer).enable_http()
        self._filer.put.assert_called_once_with('/config/fileservices/webdav/forceHttps', False)

    def test_disable_http(self):
        self._init_filer()
        ssl.SSL(self._filer).disable_http()
        self._filer.put.assert_called_once_with('/config/fileservices/webdav/forceHttps', True)

    def test_set_certificate(self):
        data = 'data\n'
        self._init_filer()
        self.patch_call("cterasdk.edge.ssl.FileSystem.get_local_file_info")
        mock_open = mock.mock_open(read_data=data)
        with mock.patch("builtins.open", mock_open):
            ssl.SSL(self._filer).set_certificate(self._private_key, self._domain_cert, self._intermediate, self._ca)
            self._filer.put.assert_called_once_with('/config/certificate', '\n' + data * 4)

    def test_get_storage_ca(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).get_storage_ca()
        self._filer.get.assert_called_once_with('/status/extStorageTrustedCA')
        self.assertEqual(ret, get_response)

    def test_set_storage_ca(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ret = ssl.SSL(self._filer).set_storage_ca(self._certificate)
        expected_param = Object()
        expected_param._classname = 'ExtTrustedCA'  # pylint: disable=protected-access
        expected_param.certificate = self._certificate
        self._filer.put.assert_called_once_with('/config/extStorageTrustedCA', mock.ANY)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_remove_storage_ca(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ssl.SSL(self._filer).remove_storage_ca()
        self._filer.put.assert_called_once_with('/config/extStorageTrustedCA', None)
