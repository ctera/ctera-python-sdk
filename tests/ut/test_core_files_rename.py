import unittest.mock as mock

from tests.ut import base_core_services


class BaseCoreServicesFilesRename(base_core_services.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._current_filename = 'Renamed Text Document.txt'
        self._new_filename = 'New Text Document.txt'
        self._parent_directory = 'My Files/Documents'

    def test_rename(self):
        execute_response = 'Success'
        self._init_services(execute_response=execute_response)
        ret = self._services.files.rename(self._parent_directory + '/' + self._current_filename, self._new_filename)
        self._services.execute.assert_called_once_with('', 'moveResources', mock.ANY)
        expected_param = self._create_rename_resource_param()
        actual_param = self._services.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, execute_response)

    def _create_rename_resource_param(self):
        sources = [self._parent_directory + '/' + self._current_filename]
        destinations = [self._parent_directory + '/' + self._new_filename]
        return self._create_action_resource_param(sources, destinations)
