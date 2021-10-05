from unittest import mock

from cterasdk import exception
from cterasdk.common import Object
from cterasdk.edge import nfs
from cterasdk.edge.enum import Mode
from tests.ut import base_edge


class TestEdgeNFS(base_edge.BaseEdgeTest):

    def test_get_configuration(self):
        self._init_filer(get_response=TestEdgeNFS._get_nfs_configuration_response())
        ret = nfs.NFS(self._filer).get_configuration()
        self._filer.get.assert_called_once_with('/config/fileservices/nfs')
        self._assert_equal_objects(ret, TestEdgeNFS._get_nfs_configuration_response())

    def test_nfs_is_disabled(self):
        self._init_filer(get_response=Mode.Disabled)
        ret = nfs.NFS(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/nfs/mode')
        self.assertEqual(ret, True)

    def test_nfs_is_not_disabled(self):
        self._init_filer(get_response=Mode.Enabled)
        ret = nfs.NFS(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/nfs/mode')
        self.assertEqual(ret, False)

    def test_disable_nfs(self):
        self._init_filer()
        nfs.NFS(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/fileservices/nfs/mode', Mode.Disabled)

    def test_enable_nfs(self):
        self._init_filer()
        nfs.NFS(self._filer).enable()
        self._filer.put.assert_called_once_with('/config/fileservices/nfs/mode', Mode.Enabled)

    def test_modify_success(self):
        self._init_filer(get_response=TestEdgeNFS._get_nfs_configuration_response())
        params = {
            'async_write': False,
            'aggregate_writes': False,
            'statd_port': 12345
        }
        nfs.NFS(self._filer).modify(**params)
        self._filer.get.assert_called_once_with('/config/fileservices/nfs')
        self._filer.put.assert_called_once_with('/config/fileservices/nfs', mock.ANY)
        expected_param = TestEdgeNFS._get_nfs_configuration_response(**params)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_raise(self):
        param = Object()
        param.mode = Mode.Disabled
        self._init_filer(get_response=param)
        with self.assertRaises(exception.CTERAException) as error:
            nfs.NFS(self._filer).modify()
        self.assertEqual('NFS must be enabled in order to modify its configuration', error.exception.message)

    @staticmethod
    def _get_nfs_configuration_response(async_write=True, aggregate_writes=True, statd_port=None):
        obj = Object()
        obj.mode = Mode.Enabled
        setattr(obj, 'async', Mode.Enabled if async_write else Mode.Disabled)
        obj.aggregateWrites = Mode.Enabled if aggregate_writes else Mode.Disabled
        if statd_port is not None:
            obj.statdPort = statd_port
        return obj
