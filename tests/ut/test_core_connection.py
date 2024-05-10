import munch
from cterasdk.core import connection
from tests.ut import base_core


class TestCoreConnection(base_core.BaseCoreTest):

    def test_run_cli_command(self):
        name = 'name'
        version = 'version'
        get_response = munch.Munch({'version': version, 'name': name})
        self._init_setup(get_response=get_response)
        self.patch_call('cterasdk.common.utils.tcp_connect')
        ret = connection.Connection(self._global_admin).test()
        self._global_admin.ctera.get.assert_called_once_with('/public/publicInfo')
        self.assertEqual(ret.name, name)
