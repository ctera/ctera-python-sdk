from tests.ut.core.user import base_user


class BaseCoreServicesFilesVersions(base_user.BaseCoreServicesTest):

    def test_list_versions(self):
        directory = 'My Files'
        execute_response = 'Success'
        self._init_services(execute_response=execute_response)
        ret = self._services.files.versions(directory)
        self._services.api.execute.assert_called_once_with('', 'listSnapshots', f'{self._base}/{directory}')
        self.assertEqual(ret, execute_response)
