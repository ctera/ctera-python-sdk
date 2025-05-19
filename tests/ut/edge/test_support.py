import datetime

from pathlib import Path
from freezegun import freeze_time

from cterasdk import exceptions
from cterasdk.edge import support
from tests.ut.edge import base_edge

import cterasdk.settings


class TestEdgeSupport(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._levels = ['cttp', 'samba', 'auth']
        self._debug_command = 'dbg level' + ' ' + ' '.join(self._levels)

    def test_set_debug_level(self):
        self._init_filer()
        support.Support(self._filer).set_debug_level(*self._levels)
        self._filer.api.execute.assert_called_once_with('/config/device', 'debugCmd', self._debug_command)

    def test_set_debug_level_input_error(self):
        self._init_filer()
        with self.assertRaises(exceptions.InputError) as error:
            support.Support(self._filer).set_debug_level(*['Expected Failure'])
        self.assertEqual('Invalid debug level', error.exception.message)

    def test_get_support_report(self):
        cterasdk.settings.io.downloads = '~'
        current_datetime = datetime.datetime.now()
        handle_response = 'Stream'
        self._init_filer(handle_response=handle_response)
        mock_save_file = self.patch_call("cterasdk.lib.storage.synfs.write")
        with freeze_time(current_datetime):
            support.Support(self._filer).get_support_report()
            self._filer.api.handle.assert_called_once_with('/supportreport')
            filename = 'Support-' + current_datetime.strftime('_%Y-%m-%dT%H_%M_%S') + '.zip'
            mock_save_file.assert_called_once_with(Path('~').expanduser(), filename, handle_response)
