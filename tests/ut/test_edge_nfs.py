from cterasdk.edge import nfs
from cterasdk.edge.enum import Mode
from tests.ut import base_edge


class TestEdgeNFS(base_edge.BaseEdgeTest):

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
