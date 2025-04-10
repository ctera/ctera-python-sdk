from cterasdk.core import reports
from cterasdk import exceptions
from tests.ut.core.admin import base_admin


class TestCoreReports(base_admin.BaseCoreTest):

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

    def test_generate_report_success(self):
        name = 'folderGroupsStatisticsReport'
        reports.Reports(self._global_admin).generate(name)
        self._global_admin.api.execute.assert_called_once_with('', 'generateReport', name)

    def test_generate_report_failure(self):
        with self.assertRaises(exceptions.InputError) as error:
            reports.Reports(self._global_admin).generate('Expected Failure')
        self.assertEqual('Invalid report type', error.exception.message)

    def _assert_called_once_with(self, report_name):
        self._global_admin.api.get.assert_called_once_with(f'/reports/{report_name}')
