from unittest import mock

from cterasdk.edge import drive
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeDrive(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._drive_name = 'XVD2'

    def test_get_all_drives(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = drive.Drive(self._filer).get()
        self._filer.get.assert_called_once_with('/config/storage/disks')
        self.assertEqual(ret, get_response)

    def test_get_drive(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = drive.Drive(self._filer).get(self._drive_name)
        self._filer.get.assert_called_once_with('/config/storage/disks/' + self._drive_name)
        self.assertEqual(ret, get_response)

    def test_format_drive(self):
        self._init_filer()
        drive.Drive(self._filer).format(self._drive_name)
        self._filer.execute.assert_called_once_with('/proc/storage', 'format', mock.ANY)

        expected_param = Object()
        expected_param.name = self._drive_name
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

    def test_format_all_drives(self):
        self._init_filer(get_response=self._get_drives_param())
        drive.Drive(self._filer).format_all()
        self._filer.get.assert_called_once_with('/status/storage/disks')

        expected_param = Object()
        expected_param.name = self._drive_name
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

    def _get_drives_param(self):
        drive_param = Object()
        drive_param.name = self._drive_name
        drives = [drive_param]
        return drives
