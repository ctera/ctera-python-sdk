import datetime
from unittest import mock

from cterasdk import exception, config
from cterasdk.edge import support
from tests.ut import base_edge


class TestEdgeSupport(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._levels = ['cttp', 'samba', 'auth']
        self._debug_command = 'dbg level' + ' ' + ' '.join(self._levels)
        self._current_datetime = datetime.datetime.now()

    def test_set_debug_level(self):
        self._init_filer()
        support.Support(self._filer).set_debug_level(*self._levels)
        self._filer.execute.assert_called_once_with('/config/device', 'debugCmd', self._debug_command)

    def test_set_debug_level_input_error(self):
        self._init_filer()
        with self.assertRaises(exception.InputError) as error:
            support.Support(self._filer).set_debug_level(*['Expected Failure'])
        self.assertEqual('Invalid debug level', error.exception.message)

    def test_get_support_report(self):
        openfile_response = 'Stream'
        self._init_filer(openfile_response=openfile_response)
        mock_save_file = self.patch_call("cterasdk.lib.filesystem.FileSystem.save")
        with mock.patch.object(datetime, 'datetime', mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = self._current_datetime
            support.Support(self._filer).get_support_report()
            self._filer.openfile.assert_called_once_with('/supportreport')
            filename = 'Support-' + self._current_datetime.strftime('_%Y-%m-%dT%H_%M_%S') + '.zip'
            mock_save_file.assert_called_once_with(config.filesystem['dl'], filename, openfile_response)
