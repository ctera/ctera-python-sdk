from unittest import mock

from cterasdk.common import Object
from cterasdk import exceptions

from tests.ut.core.user import base_user


class BaseCoreServicesFilesMove(base_user.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._filename = 'New Text Document.txt'
        self._source = 'My Files/Documents/' + self._filename
        self._dest = 'My Files/Reports'

    def test_move_no_wait(self):
        execute_response = self._task_reference
        self._init_services(execute_response=execute_response)
        ret = self._services.files.move(self._source, destination=self._dest, wait=False)
        self._services.api.execute.assert_called_once_with('', 'moveResources', mock.ANY)
        expected_param = self._create_move_resource_param()
        actual_param = self._services.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret.ref, execute_response)

    def test_move_completed_with_warnings_raises_move_error(self):
        task = mock.MagicMock()
        task.completed = False
        task.completed_with_warnings = True
        task.failed = False
        task.cursor = None
        task.error_type = None
        task.unknown_object.return_value = True
        task.progress_str = None
        self._services.tasks.wait = mock.MagicMock(return_value=task)
        self._init_services(execute_response=self._task_reference)
        with self.assertRaises(exceptions.io.core.MoveError):
            self._services.files.move(self._source, destination=self._dest)
        self._services.tasks.wait.assert_called_once_with(self._task_reference)

    def _create_move_resource_param(self):
        destinations = [base_user.BaseCoreServicesTest.encode_path(self._dest + '/' + self._filename)]
        return self._create_action_resource_param([base_user.BaseCoreServicesTest.encode_path(self._source)], destinations)
