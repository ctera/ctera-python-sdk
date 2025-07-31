from unittest import mock

from tests.ut.core.user import base_user


class BaseCoreServicesFilesRename(base_user.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._current_filename = 'Renamed Text Document.txt'
        self._new_filename = 'New Text Document.txt'
        self._parent_directory = 'My Files/Documents'

    def test_rename(self):
        execute_response = self._task_reference
        self._init_services(execute_response=execute_response)
        ret = self._services.files.rename(f'{self._parent_directory}/{self._current_filename}', self._new_filename, wait=False)
        self._services.api.execute.assert_called_once_with('', 'moveResources', mock.ANY)
        expected_param = self._create_rename_resource_param()
        actual_param = self._services.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret.ref, execute_response)

    def _create_rename_resource_param(self):
        sources = [base_user.BaseCoreServicesTest.encode_path(self._parent_directory + '/' + self._current_filename)]
        destinations = [base_user.BaseCoreServicesTest.encode_path(self._parent_directory + '/' + self._new_filename)]
        return self._create_action_resource_param(sources, destinations)
