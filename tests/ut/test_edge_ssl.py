from unittest import mock

from cterasdk.edge import ssl
from tests.ut import base_edge


class TestEdgeSSL(base_edge.BaseEdgeTest):

    def test_is_http_disabled_true(self):
        get_response=True
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, get_response)

    def test_is_http_disabled_false(self):
        get_response=False
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, get_response)

    def test_is_http_enabled_true(self):
        get_response=False
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_enabled()
        self._filer.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, True)

    def test_is_http_enabled_false(self):
        get_response=True
        self._init_filer(get_response=get_response)
        ret = ssl.SSL(self._filer).is_enabled()
        self._filer.get.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, False)

    def test_enable_http(self):
        self._init_filer()
        ret = ssl.SSL(self._filer).enable_http()
        self._filer.put.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, False)

    def test_disable_http(self):
        self._init_filer()
        ret = ssl.SSL(self._filer).enable_http()
        self._filer.put.assert_called_once_with('/config/fileservices/webdav/forceHttps')
        self._assert_equal_objects(ret, True)
