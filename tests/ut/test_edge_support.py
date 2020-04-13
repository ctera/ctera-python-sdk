from cterasdk import exception
from cterasdk.edge import support
from tests.ut import base_edge


class TestEdgeSupport(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._levels = ['cttp', 'samba', 'auth']
        self._debug_command = 'dbg level' + ' ' + ' '.join(self._levels)

    def test_set_debug_level(self):
        self._init_filer()
        support.Support(self._filer).set_debug_level(*self._levels)
        self._filer.execute.assert_called_once_with('/config/device', 'debugCmd', self._debug_command)

    def test_set_debug_level_input_error(self):
        self._init_filer()
        with self.assertRaises(exception.InputError) as error:
            support.Support(self._filer).set_debug_level(*['Expected Failure'])
        self.assertEqual('Invalid debug level', error.exception.message)
