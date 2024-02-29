from cterasdk.core import reports
from tests.ut import base_core


class TestCoreReports(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._get_response = 'Success'
        self._init_global_admin(get_response=self._get_response)

    def test_storage_report(self):
        ret = reports.Reports(self._global_admin).storage()
        self._assert_called_once_with('storageLocationsStatisticsReport')
        self.assertEqual(ret, self._get_response)

    def test_portals_report(self):
        ret = reports.Reports(self._global_admin).portals()
        self._assert_called_once_with('portalsStatisticsReport')
        self.assertEqual(ret, self._get_response)

    def test_folders_report(self):
        ret = reports.Reports(self._global_admin).folders()
        self._assert_called_once_with('foldersStatisticsReport')
        self.assertEqual(ret, self._get_response)

    def test_folder_groups_report(self):
        ret = reports.Reports(self._global_admin).folder_groups()
        self._assert_called_once_with('folderGroupsStatisticsReport')
        self.assertEqual(ret, self._get_response)

    def test_devices_report(self):
        ret = reports.Reports(self._global_admin).devices()
        self._assert_called_once_with('devicesStatisticsReport')
        self.assertEqual(ret, self._get_response)

    def _assert_called_once_with(self, report_name):
        self._global_admin.api.get.assert_called_once_with(f'/reports/{report_name}')
