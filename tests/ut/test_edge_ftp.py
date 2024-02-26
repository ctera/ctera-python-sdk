from unittest import mock

from cterasdk import exception
from cterasdk.common import Object
from cterasdk.edge import ftp
from cterasdk.edge.enum import Mode
from tests.ut import base_edge


class TestEdgeFTP(base_edge.BaseEdgeTest):

    def test_get_configuration(self):
        self._init_filer(get_response=TestEdgeFTP._get_ftp_configuration_response())
        ret = ftp.FTP(self._filer).get_configuration()
        self._filer.get.assert_called_once_with('/config/fileservices/ftp')
        self._assert_equal_objects(ret, TestEdgeFTP._get_ftp_configuration_response())

    def test_ftp_is_disabled(self):
        self._init_filer(get_response=Mode.Disabled)
        ret = ftp.FTP(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/ftp/mode')
        self.assertEqual(ret, True)

    def test_ftp_is_not_disabled(self):
        self._init_filer(get_response=Mode.Enabled)
        ret = ftp.FTP(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/ftp/mode')
        self.assertEqual(ret, False)

    def test_enable_ftp(self):
        self._init_filer()
        ftp.FTP(self._filer).enable()
        self._filer.put.assert_called_once_with('/config/fileservices/ftp/mode', Mode.Enabled)

    def test_disable_ftp(self):
        self._init_filer()
        ftp.FTP(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/fileservices/ftp/mode', Mode.Disabled)

    def test_modify_success(self):
        self._init_filer(get_response=TestEdgeFTP._get_ftp_configuration_response())
        ftp.FTP(self._filer).modify(True, 5, 'folder', 'Welcome to Gotham City FTP.', 10, True)
        self._filer.get.assert_called_once_with('/config/fileservices/ftp')
        self._filer.put.assert_called_once_with('/config/fileservices/ftp', mock.ANY)
        expected_param = TestEdgeFTP._get_ftp_configuration_response(True, 5, 'folder', 'Welcome to Gotham City FTP.', 10, True)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_raise(self):
        param = Object()
        param.mode = Mode.Disabled
        self._init_filer(get_response=param)
        with self.assertRaises(exceptions.CTERAException) as error:
            ftp.FTP(self._filer).modify()
        self.assertEqual('FTP must be enabled in order to modify its configuration', error.exception.message)

    @staticmethod
    def _get_ftp_configuration_response(allow_anonymous_ftp=None, anonymous_download_limit=None, anonymous_ftp_folder=None,
                                        banner_message=None, max_connections_per_ip=None, require_ssl=None):
        obj = Object()
        obj.mode = Mode.Enabled
        obj.AnonymousDownloadLimit = anonymous_download_limit if anonymous_download_limit is not None else None
        obj.AnonymousFTPFolder = anonymous_ftp_folder if anonymous_ftp_folder is not None else 'default folder'
        obj.AllowAnonymousFTP = allow_anonymous_ftp if allow_anonymous_ftp is not None else False
        obj.BannerMessage = banner_message if banner_message is not None else 'Welcome to CTERA FTP.'
        obj.MaxConnectionsPerIP = max_connections_per_ip if max_connections_per_ip is not None else 5
        obj.RequireSSL = require_ssl if require_ssl is not None else False
        return obj
