from cterasdk.core import domains
from tests.ut import base_core


class TestCoreDomains(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._domains = ['na.ctera.local', 'eu.ctera.local']

    def test_list_domains(self):
        get_response = self._domains
        self._init_global_admin(get_response=get_response)
        ret = domains.Domains(self._global_admin).list_domains()
        self._global_admin.api.get.assert_called_once_with('/domains')
        self.assertEqual(ret, get_response)
