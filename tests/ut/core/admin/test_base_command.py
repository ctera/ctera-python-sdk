from tests.ut.core.admin import base_admin
from cterasdk.core import base_command


class TestCoreBaseCommand(base_admin.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._mock_session = self.patch_call("cterasdk.objects.services.Management.session")

    def test_get_session(self):
        response = 'Success'
        self._mock_session.return_value = response
        self._init_global_admin()
        ret = base_command.BaseCommand(self._global_admin).session()
        self.assertEqual(ret, response)
