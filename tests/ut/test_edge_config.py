import datetime
from unittest import mock

from cterasdk.edge import config
from tests.ut import base_edge

import cterasdk.settings


class TestEdgeConfig(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._hostname = 'vGateway-01dc'
        self._location = '205 E. 42nd St. New York, NY. 10017'
        self._filename = 'file.xml'
        self._target_directory = '/path/to/folder'
        self._default_download_directory = cterasdk.settings.downloads.location
        self._current_datetime = datetime.datetime.now()

    def test_get_hostname(self):
        self._init_filer(get_response=self._hostname)
        ret = config.Config(self._filer).get_hostname()
        self._filer.api.get.assert_called_once_with('/config/device/hostname')
        self.assertEqual(ret, self._hostname)

    def test_set_hostname(self):
        self._init_filer(put_response=self._hostname)
        ret = config.Config(self._filer).set_hostname(self._hostname)
        self._filer.api.put.assert_called_once_with('/config/device/hostname', self._hostname)
        self.assertEqual(ret, self._hostname)

    def test_get_location(self):
        self._init_filer(get_response=self._location)
        ret = config.Config(self._filer).get_location()
        self._filer.api.get.assert_called_once_with('/config/device/location')
        self.assertEqual(ret, self._location)

    def test_set_location(self):
        self._init_filer(put_response=self._location)
        ret = config.Config(self._filer).set_location(self._location)
        self._filer.api.put.assert_called_once_with('/config/device/location', self._location)
        self.assertEqual(ret, self._location)

    def test_is_wizard_enabled(self):
        get_response = True
        self._init_filer(get_response=get_response)
        ret = config.Config(self._filer).is_wizard_enabled()
        self._filer.api.get.assert_called_once_with('/config/gui/openFirstTimeWizard')
        self.assertEqual(ret, get_response)

    def test_enable_first_time_wizard(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ret = config.Config(self._filer).enable_wizard()
        self._filer.api.put.assert_called_once_with('/config/gui/openFirstTimeWizard', True)
        self.assertEqual(ret, put_response)

    def test_disable_first_time_wizard(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ret = config.Config(self._filer).disable_wizard()
        self._filer.api.put.assert_called_once_with('/config/gui/openFirstTimeWizard', False)
        self.assertEqual(ret, put_response)

    def test_edge_config_export_default_dest(self):
        handle_response = 'Stream'
        self._init_filer(handle_response=handle_response)
        mock_get_dirpath = self.patch_call("cterasdk.lib.filesystem.FileSystem.get_dirpath",
                                           return_value=self._default_download_directory)
        mock_save_file = self.patch_call("cterasdk.lib.filesystem.FileSystem.save")
        with mock.patch.object(datetime, 'datetime', mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = self._current_datetime
            config.Config(self._filer).export()
            self._filer.openfile.assert_called_once_with('/export')
            mock_get_dirpath.assert_called_once()
            mock_save_file.assert_called_once_with(self._default_download_directory,
                                                   self._current_datetime.strftime('_%Y-%m-%dT%H_%M_%S.xml'), handle_response)

    def test_edge_config_export_target_directory_default_filename(self):
        handle_response = 'Stream'
        self._init_filer(handle_response=handle_response)
        mock_get_dirpath = self.patch_call("cterasdk.lib.filesystem.FileSystem.split_file_directory",
                                           return_value=(self._target_directory, None))
        mock_save_file = self.patch_call("cterasdk.lib.filesystem.FileSystem.save")
        with mock.patch.object(datetime, 'datetime', mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = self._current_datetime
            config.Config(self._filer).export(self._target_directory)
            self._filer.openfile.assert_called_once_with('/export')
            mock_get_dirpath.assert_called_once()
            mock_save_file.assert_called_once_with(self._target_directory,
                                                   self._current_datetime.strftime('_%Y-%m-%dT%H_%M_%S.xml'), handle_response)
