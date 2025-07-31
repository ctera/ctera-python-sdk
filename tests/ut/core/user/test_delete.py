from unittest import mock

from tests.ut.core.user import base_user


class BaseCoreServicesFilesDelete(base_user.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._path = 'My Files/Documents'

    def test_delete_no_wait(self):
        execute_response = self._task_reference
        self._init_services(execute_response=execute_response)
        ret = self._services.files.delete(self._path, wait=False)
        self._services.api.execute.assert_called_once_with('', 'deleteResources', mock.ANY)
        expected_param = self._create_delete_resource_param()
        actual_param = self._services.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret.ref, execute_response)

    def _create_delete_resource_param(self):
        return self._create_action_resource_param([base_user.BaseCoreServicesTest.encode_path(self._path)])
