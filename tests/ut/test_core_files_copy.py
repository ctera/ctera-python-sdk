import unittest.mock as mock

from tests.ut import base_core_services


class BaseCoreServicesFilesCopy(base_core_services.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._filename = 'New Text Document.txt'
        self._source = 'My Files/Documents/' + self._filename
        self._dest = 'My Files/Reports'

    def test_copy(self):
        execute_response = 'Success'
        self._init_services(execute_response=execute_response)
        ret = self._services.files.copy(self._source, self._dest)
        self._services.execute.assert_called_once_with('', 'copyResources', mock.ANY)
        expected_param = self._create_copy_resource_param()
        actual_param = self._services.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, execute_response)

    def _create_copy_resource_param(self):
        destinations = [self._dest + '/' + self._filename]
        return self._create_action_resource_param([self._source], destinations)
