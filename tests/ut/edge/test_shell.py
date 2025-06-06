from unittest import mock

from cterasdk import exceptions
from cterasdk.edge import shell
from cterasdk.lib import task_manager_base
from cterasdk.common import Object
from tests.ut.edge import base_edge


class TestEdgeShell(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._shell_command = 'cat /proc/meminfo'
        self._task_id = '138'
        self._task_result = 'MemTotal: 7778104 kB'

    def test_run_shell_command(self):
        self._init_filer(execute_response=self._task_id)
        self._filer.tasks.wait = mock.MagicMock(return_value=self._get_task_manager_result_object())
        ret = shell.Shell(self._filer).run_command(self._shell_command)
        self._filer.tasks.wait.assert_called_once_with(self._task_id)
        self._filer.api.execute.assert_called_once_with('/config/device', 'bgshell', self._shell_command)
        self.assertEqual(ret, self._task_result)

    def test_run_shell_command_task_error(self):
        execute_response = self._task_id
        self._init_filer(execute_response=execute_response)
        self._filer.tasks.wait = mock.MagicMock(side_effect=task_manager_base.TaskError(self._task_id))
        with self.assertRaises(exceptions.CTERAException) as error:
            shell.Shell(self._filer).run_command(self._shell_command)
        self._filer.tasks.wait.assert_called_once_with(self._task_id)
        self.assertEqual('An error occurred while executing task', str(error.exception))

    def _get_task_manager_result_object(self):
        task_param = Object()
        task_param.result = Object()
        task_param.result.result = self._task_result
        return task_param
