import unittest.mock as mock

from tests.ut import base_core_services


class BaseCoreServicesFilesUndelete(base_core_services.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._path = 'My Files/Documents'

    def test_undelete(self):
        execute_response = 'Success'
        self._init_services(execute_response=execute_response)
        ret = self._services.files.undelete(self._path)
        self._services.execute.assert_called_once_with('', 'restoreResources', mock.ANY)
        expected_param = self._create_undelete_resource_param()
        actual_param = self._services.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, execute_response)

    def _create_undelete_resource_param(self):
        return self._create_action_resource_param([self._path])
