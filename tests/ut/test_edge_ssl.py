from unittest import mock

from cterasdk.edge import ssl
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeSSL(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._key_filepath = './certs/private.key'
        self._domain_cert = './certs/certificate.crt'
        self._intermediate_cert = './certs/intermediate.crt'
        self._root_cert = './certs/ca.crt'

        self._private_key_contents = 'private_key'
        self._certificate_contents = 'certificate'

    def test_is_http_disabled_true(self):
        get_response = True
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_http_disabled()
        self._filer.api.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, get_response)

    def test_is_http_disabled_false(self):
        get_response = False
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_http_disabled()
        self._filer.api.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, get_response)

    def test_is_http_enabled_true(self):
        get_response = False
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_http_enabled()
        self._filer.api.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, True)

    def test_is_http_enabled_false(self):
        get_response = True
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_http_enabled()
        self._filer.api.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, False)

    def test_enable_http(self):
        self._init_filer()
        ssl.SSL(self._filer).enable_http()
        self._filer.api.put.assert_called_once_with('/config/fileservices/webdav/forceHttps', False)

    def test_disable_http(self):
        self._init_filer()
        ssl.SSL(self._filer).disable_http()
        self._filer.api.put.assert_called_once_with('/config/fileservices/webdav/forceHttps', True)

    def test_import_certificate(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        mock_load_private_key = self.patch_call("cterasdk.lib.crypto.PrivateKey.load_private_key")
        mock_load_private_key.return_value = TestEdgeSSL._get_secret(self._private_key_contents)
        mock_load_certificate = self.patch_call("cterasdk.lib.crypto.X509Certificate.load_certificate")
        mock_load_certificate.return_value = TestEdgeSSL._get_secret(self._certificate_contents)
        ret = ssl.SSLv1(self._filer).import_certificate(self._key_filepath, self._domain_cert, self._intermediate_cert, self._root_cert)
        mock_load_private_key.assert_called_once_with(self._key_filepath)
        mock_load_certificate.assert_has_calls(
            [
                mock.call(self._domain_cert),
                mock.call(self._intermediate_cert),
                mock.call(self._root_cert),
            ]
        )
        expected_param = ''.join([
            self._private_key_contents,
            self._certificate_contents,
            self._certificate_contents,
            self._certificate_contents
        ])
        self._filer.api.put.assert_called_once_with('/config/certificate', f'\n{expected_param}')
        self.assertEqual(ret, put_response)

    def test_get_storage_ca(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = ssl.SSLv1(self._filer).get_storage_ca()
        self._filer.api.get.assert_called_once_with('/status/extStorageTrustedCA')
        self.assertEqual(ret, get_response)

    def test_import_storage_ca(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        mock_load_certificate = self.patch_call("cterasdk.lib.crypto.X509Certificate.load_certificate")
        mock_load_certificate.return_value = TestEdgeSSL._get_secret(self._certificate_contents)
        ret = ssl.SSLv1(self._filer).import_storage_ca(self._domain_cert)
        expected_param = Object()
        expected_param._classname = 'ExtTrustedCA'  # pylint: disable=protected-access
        expected_param.certificate = self._certificate_contents
        mock_load_certificate.assert_called_once_with(self._domain_cert)
        self._filer.api.put.assert_called_once_with('/config/extStorageTrustedCA', mock.ANY)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_remove_storage_ca(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ssl.SSLv1(self._filer).remove_storage_ca()
        self._filer.api.put.assert_called_once_with('/config/extStorageTrustedCA', None)

    @staticmethod
    def _get_secret(secret):
        param = Object()
        param.pem_data = secret.encode('utf-8')
        param.subject = 'subject'
        param.issuer = 'issuer'
        return param
