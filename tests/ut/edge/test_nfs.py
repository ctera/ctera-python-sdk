from unittest import mock

from cterasdk import exceptions
from cterasdk.common import Object
from cterasdk.edge import nfs
from cterasdk.edge.enum import Mode
from tests.ut.edge import base_edge


class TestEdgeNFS(base_edge.BaseEdgeTest):

    def test_get_configuration(self):
        self._init_filer(get_response=TestEdgeNFS._get_nfs_configuration_response())
        ret = nfs.NFS(self._filer).get_configuration()
        self._filer.api.get.assert_called_once_with('/config/fileservices/nfs')
        self._assert_equal_objects(ret, TestEdgeNFS._get_nfs_configuration_response())

    def test_nfs_is_disabled(self):
        self._init_filer(get_response=Mode.Disabled)
        ret = nfs.NFS(self._filer).is_disabled()
        self._filer.api.get.assert_called_once_with('/config/fileservices/nfs/mode')
        self.assertEqual(ret, True)

    def test_nfs_is_not_disabled(self):
        self._init_filer(get_response=Mode.Enabled)
        ret = nfs.NFS(self._filer).is_disabled()
        self._filer.api.get.assert_called_once_with('/config/fileservices/nfs/mode')
        self.assertEqual(ret, False)

    def test_disable_nfs(self):
        self._init_filer()
        nfs.NFS(self._filer).disable()
        self._filer.api.put.assert_called_once_with('/config/fileservices/nfs/mode', Mode.Disabled)

    def test_enable_nfs(self):
        self._init_filer()
        nfs.NFS(self._filer).enable()
        self._filer.api.put.assert_called_once_with('/config/fileservices/nfs/mode', Mode.Enabled)

    def test_modify_success(self):
        self._init_filer(get_response=TestEdgeNFS._get_nfs_configuration_response())
        params = {
            'async_write': False,
            'aggregate_writes': False,
            'statd_port': 12345
        }
        nfs.NFS(self._filer).modify(**params)
        self._filer.api.get.assert_called_once_with('/config/fileservices/nfs')
        self._filer.api.put.assert_called_once_with('/config/fileservices/nfs', mock.ANY)
        expected_param = TestEdgeNFS._get_nfs_configuration_response(**params)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_raise(self):
        param = Object()
        param.mode = Mode.Disabled
        self._init_filer(get_response=param)
        with self.assertRaises(exceptions.CTERAException) as error:
            nfs.NFS(self._filer).modify()
        self.assertEqual('NFS must be enabled in order to modify its configuration', str(error.exception))

    def test_modify_all_parameters(self):
        """Test modifying all NFS parameters"""
        self._init_filer(get_response=TestEdgeNFS._get_nfs_configuration_response())
        params = {
            'async_write': False,
            'aggregate_writes': False,
            'mountd_port': 1234,
            'statd_port': 5678,
            'nfsv4_enabled': True,
            'krb5_enabled': True,
            'nfsd_host': '192.168.1.1'
        }
        nfs.NFS(self._filer).modify(**params)
        self._filer.api.get.assert_called_once_with('/config/fileservices/nfs')
        self._filer.api.put.assert_called_once_with('/config/fileservices/nfs', mock.ANY)
        actual_param = self._filer.api.put.call_args[0][1]
        self.assertEqual(actual_param.mountdPort, params['mountd_port'])
        self.assertEqual(actual_param.nfsv4enabled, params['nfsv4_enabled'])
        self.assertEqual(actual_param.krb5, params['krb5_enabled'])
        self.assertEqual(actual_param.nfsHost, params['nfsd_host'])

    def test_modify_krb5_without_nfsv4(self):
        """Test enabling Kerberos without NFSv4 enabled"""
        config = TestEdgeNFS._get_nfs_configuration_response()
        config.nfsv4enabled = False
        self._init_filer(get_response=config)

        with self.assertRaises(exceptions.CTERAException) as error:
            nfs.NFS(self._filer).modify(krb5_enabled=True)
        self.assertEqual('NFSv4 must be enabled in order to enable Kerberos', str(error.exception))

    @staticmethod
    def _get_nfs_configuration_response(
            async_write=True,
            aggregate_writes=True,
            statd_port=None,
            mountd_port=None,
            nfsv4_enabled=None,
            krb5_enabled=None,
            nfsd_host=None):
        """Extended helper method to support all configuration parameters"""
        obj = Object()
        obj.mode = Mode.Enabled
        setattr(obj, 'async', Mode.Enabled if async_write else Mode.Disabled)
        obj.aggregateWrites = Mode.Enabled if aggregate_writes else Mode.Disabled
        if statd_port is not None:
            obj.statdPort = statd_port
        if mountd_port is not None:
            obj.mountdPort = mountd_port
        if nfsv4_enabled is not None:
            obj.nfsv4enabled = nfsv4_enabled
        if krb5_enabled is not None:
            obj.krb5 = krb5_enabled
        if nfsd_host is not None:
            obj.nfsHost = nfsd_host
        return obj
