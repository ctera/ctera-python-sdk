from cterasdk.edge import groups
from tests.ut import base_edge


class TestEdgeGroups(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._group_name = 'group'

    def test_get_all_group(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = groups.Groups(self._filer).get()
        self._filer.get.assert_called_once_with('/config/auth/groups')
        self.assertEqual(ret, get_response)

    def test_get_group(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = groups.Groups(self._filer).get(self._group_name)
        self._filer.get.assert_called_once_with('/config/auth/groups/' + self._group_name)
        self.assertEqual(ret, get_response)
