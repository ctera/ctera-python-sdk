from unittest import mock

from tests.ut.core.user import base_user


class BaseCoreServicesFilesUndelete(base_user.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._path = 'My Files/Documents'

    def test_undelete(self):
        execute_response = 'Success'
        self._init_services(execute_response=execute_response)
        ret = self._services.files.undelete(self._path)
        self._services.api.execute.assert_called_once_with('', 'restoreResources', mock.ANY)
        expected_param = self._create_undelete_resource_param()
        actual_param = self._services.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, execute_response)

    def _create_undelete_resource_param(self):
        return self._create_action_resource_param([self.encode_path(self._path)])
