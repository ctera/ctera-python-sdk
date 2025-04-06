import munch
from cterasdk.core import connection
from tests.ut.core.admin import base_admin


class TestCoreConnection(base_admin.BaseCoreTest):

    def test_run_cli_command(self):
        name = 'name'
        version = 'version'
        get_response = munch.Munch({'version': version, 'name': name})
        self.patch_call('cterasdk.core.connection.tcp_connect')
        self._init_setup(get_response=get_response)
        ret = connection.test(self._global_admin)
        self._global_admin.ctera.get.assert_called_once_with('/public/publicInfo')
        self.assertEqual(ret.name, name)
