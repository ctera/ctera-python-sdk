from cterasdk.edge import rsync
from cterasdk.edge.enum import Mode
from tests.ut import base_edge


class TestEdgeRSync(base_edge.BaseEdgeTest):

    def test_rsync_is_disabled(self):
        self._init_filer(get_response=Mode.Disabled)
        ret = rsync.RSync(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/rsync/server')
        self.assertEqual(ret, True)

    def test_rsync_is_not_disabled(self):
        self._init_filer(get_response=Mode.Enabled)
        ret = rsync.RSync(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/rsync/server')
        self.assertEqual(ret, False)

    def test_disable_rsync(self):
        self._init_filer()
        rsync.RSync(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/fileservices/rsync/server', Mode.Disabled)
