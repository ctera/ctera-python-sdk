from unittest import mock

from cterasdk import exceptions
from cterasdk.common import Object
from cterasdk.edge import rsync
from cterasdk.edge.enum import Mode
from tests.ut.edge import base_edge


class TestEdgeRSync(base_edge.BaseEdgeTest):

    def test_get_configuration(self):
        self._init_filer(get_response=TestEdgeRSync._get_rsync_configuration_response())
        ret = rsync.RSync(self._filer).get_configuration()
        self._filer.api.get.assert_called_once_with('/config/fileservices/rsync')
        self._assert_equal_objects(ret, TestEdgeRSync._get_rsync_configuration_response())

    def test_rsync_is_disabled(self):
        self._init_filer(get_response=Mode.Disabled)
        ret = rsync.RSync(self._filer).is_disabled()
        self._filer.api.get.assert_called_once_with('/config/fileservices/rsync/server')
        self.assertEqual(ret, True)

    def test_rsync_is_not_disabled(self):
        self._init_filer(get_response=Mode.Enabled)
        ret = rsync.RSync(self._filer).is_disabled()
        self._filer.api.get.assert_called_once_with('/config/fileservices/rsync/server')
        self.assertEqual(ret, False)

    def test_enable_ftp(self):
        self._init_filer()
        rsync.RSync(self._filer).enable()
        self._filer.api.put.assert_called_once_with('/config/fileservices/rsync/server', Mode.Enabled)

    def test_disable_rsync(self):
        self._init_filer()
        rsync.RSync(self._filer).disable()
        self._filer.api.put.assert_called_once_with('/config/fileservices/rsync/server', Mode.Disabled)

    def test_modify_success(self):
        port = 999
        max_connections = 50
        self._init_filer(get_response=TestEdgeRSync._get_rsync_configuration_response())
        rsync.RSync(self._filer).modify(port, max_connections)
        self._filer.api.get.assert_called_once_with('/config/fileservices/rsync')
        self._filer.api.put.assert_called_once_with('/config/fileservices/rsync', mock.ANY)
        expected_param = TestEdgeRSync._get_rsync_configuration_response(port, max_connections)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_raise(self):
        param = Object()
        param.server = Mode.Disabled
        self._init_filer(get_response=param)
        with self.assertRaises(exceptions.CTERAException) as error:
            rsync.RSync(self._filer).modify()
        self.assertEqual('RSync must be enabled in order to modify its configuration', error.exception.message)

    @staticmethod
    def _get_rsync_configuration_response(port=None, max_connections=None):
        obj = Object()
        obj.server = Mode.Enabled
        obj.port = port if port is not None else 873
        obj.maxConnections = max_connections if max_connections is not None else 10
        return obj
