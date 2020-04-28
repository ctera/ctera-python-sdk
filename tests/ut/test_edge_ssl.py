from unittest import mock

from cterasdk.edge import ssl
from tests.ut import base_edge


class TestEdgeSSL(base_edge.BaseEdgeTest):

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

    def test_upload_cert_reboot_no_wait(self):
        data = 'data'
        self._init_filer()
        self.patch_call("cterasdk.edge.ssl.FileSystem.get_local_file_info")
        mock_open = mock.mock_open(read_data=data)
        with mock.patch("builtins.open", mock_open):
            self._filer.power.reboot = mock.MagicMock()
            ssl.SSL(self._filer).upload_cert(data, data)
            self._filer.put.assert_called_once_with('/config/certificate', '\n' + data + data)
            self._filer.power.reboot.assert_called_once_with(False)

    def test_upload_cert_no_reboot(self):
        data = 'data'
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        self.patch_call("cterasdk.edge.ssl.FileSystem.get_local_file_info")
        mock_open = mock.mock_open(read_data=data)
        with mock.patch("builtins.open", mock_open):
            ret = ssl.SSL(self._filer).upload_cert(data, data, False)
            self._filer.put.assert_called_once_with('/config/certificate', '\n' + data + data)
            self.assertEqual(ret, put_response)
