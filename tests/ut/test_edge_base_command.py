from tests.ut import base_edge
from cterasdk.edge import base_command


class TestEdgeBaseCommand(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._mock_session = self.patch_call("cterasdk.objects.services.Management.session")

    def test_get_session(self):
        response = 'Success'
        self._mock_session.return_value = response
        self._init_filer()
        ret = base_command.BaseCommand(self._filer).session()
        self.assertEqual(ret, response)
