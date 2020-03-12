from cterasdk.edge import afp
from cterasdk.edge.enum import Mode
from tests.ut import base_edge


class TestEdgeAFP(base_edge.BaseEdgeTest):

    def test_afp_is_disabled(self):
        self._init_filer(get_response=Mode.Disabled)
        ret = afp.AFP(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/afp/mode')
        self.assertEqual(ret, True)

    def test_afp_is_not_disabled(self):
        self._init_filer(get_response=Mode.Enabled)
        ret = afp.AFP(self._filer).is_disabled()
        self._filer.get.assert_called_once_with('/config/fileservices/afp/mode')
        self.assertEqual(ret, False)

    def test_disable_afp(self):
        self._init_filer()
        afp.AFP(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/fileservices/afp/mode', Mode.Disabled)
