from cterasdk.edge import ftp
from cterasdk.edge.enum import Mode
from tests.ut import base_edge


class TestEdgeFTP(base_edge.BaseEdgeTest):

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

    def test_disable_ftp(self):
        self._init_filer()
        ftp.FTP(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/fileservices/ftp/mode', Mode.Disabled)
