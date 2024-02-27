from cterasdk.edge import cli
from tests.ut import base_edge


class TestEdgeCLI(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._cli_command = 'show /config/fileservices/cifs'

    def test_run_cli_command(self):
        execute_response = 'Success'
        self._init_filer(execute_response=execute_response)
        ret = cli.CLI(self._filer).run_command(self._cli_command)
        self._filer.api.execute.assert_called_once_with('/config/device', 'debugCmd', self._cli_command)
        self.assertEqual(ret, execute_response)
