from unittest import mock

from cterasdk.edge import groups
from cterasdk.edge.enum import PrincipalType
from cterasdk.edge.types import UserGroupEntry
from tests.ut import base_edge


class TestEdgeGroups(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._group_name = 'group'
        self._domain_user = UserGroupEntry(PrincipalType.DU, 'bruce.wayne@we.com')

    def test_get_all_group(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = groups.Groups(self._filer).get()
        self._filer.api.get.assert_called_once_with('/config/auth/groups')
        self.assertEqual(ret, get_response)

    def test_get_group(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = groups.Groups(self._filer).get(self._group_name)
        self._filer.api.get.assert_called_once_with('/config/auth/groups/' + self._group_name)
        self.assertEqual(ret, get_response)

    def test_add_members(self):
        self._init_filer(get_response=[])
        groups.Groups(self._filer).add_members(self._group_name, [self._domain_user])
        self._filer.api.get.assert_called_once_with(f'/config/auth/groups/{self._group_name}/members')
        self._filer.api.put.assert_called_once_with(f'/config/auth/groups/{self._group_name}/members', mock.ANY)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, [self._domain_user.to_server_object()])

    def test_remove_members(self):
        self._init_filer(get_response=[self._domain_user.to_server_object()])
        groups.Groups(self._filer).remove_members(self._group_name, [self._domain_user])
        self._filer.api.get.assert_called_once_with(f'/config/auth/groups/{self._group_name}/members')
        self._filer.api.put.assert_called_once_with(f'/config/auth/groups/{self._group_name}/members', mock.ANY)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, [])
