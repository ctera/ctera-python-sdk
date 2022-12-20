from cterasdk.core import cli
from tests.ut import base_core


class TestCoreCLI(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._cli_command = 'show /settings'

    def test_run_cli_command(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = cli.CLI(self._global_admin).run_command(self._cli_command)
        self._global_admin.execute.assert_called_once_with('', 'debugCmd', self._cli_command)
        self.assertEqual(ret, execute_response)
