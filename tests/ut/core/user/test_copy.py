from unittest import mock

from tests.ut.core.user import base_user


class BaseCoreServicesFilesCopy(base_user.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._filename = 'New Text Document.txt'
        self._source = 'My Files/Documents/' + self._filename
        self._dest = 'My Files/Reports'

    def test_copy(self):
        execute_response = 'Success'
        self._init_services(execute_response=execute_response)
        ret = self._services.files.copy(self._source, destination=self._dest)
        self._services.api.execute.assert_called_once_with('', 'copyResources', mock.ANY)
        expected_param = self._create_copy_resource_param()
        actual_param = self._services.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, execute_response)

    def _create_copy_resource_param(self):
        destinations = [self.encode_path(self._dest + '/' + self._filename)]
        return self._create_action_resource_param([self.encode_path(self._source)], destinations)
