# pylint: disable=protected-access
from unittest import mock

from cterasdk import exception
from cterasdk.common import Object
from cterasdk.core.types import GroupAccount
from cterasdk.core import groups
from tests.ut import base_core


class TestCoreGroups(base_core.BaseCoreTest):

    # pylint: disable=too-many-instance-attributes
    def setUp(self):
        super().setUp()
        self._group_class_name = 'PortalGroup'
        self._groupname = 'groupname'
        self._description = 'this is a test group'
        self._domain = 'ctera.local'
        self._local_group = GroupAccount(self._groupname)
        self._domain_group = GroupAccount(self._groupname, self._domain)

    def test_get_local_group_success(self):
        for group_account in [self._local_group, self._domain_group]:
            get_multi_response = self._get_group_object(name=group_account.name)
            self._init_global_admin(get_multi_response=get_multi_response)
            ret = groups.Groups(self._global_admin).get(group_account)
            self._global_admin.get_multi.assert_called_once_with(self._get_group_url(group_account), mock.ANY)
            expected_include = ['/' + attr for attr in groups.Groups.default]
            actual_include = self._global_admin.get_multi.call_args[0][1]
            self.assertEqual(len(expected_include), len(actual_include))
            for attr in expected_include:
                self.assertIn(attr, actual_include)
            self.assertEqual(ret.name, group_account.name)

    def _get_group_url(self, group):
        return f'/localGroups/{group.name}' if group.is_local else f'/domains/{account.directory}/adGroups/{group_account.name}'

    def test_get_group_not_found(self):
        get_multi_response = self._get_group_object(name=None)
        self._init_global_admin(get_multi_response=get_multi_response)
        with self.assertRaises(exception.CTERAException) as error:
            groups.Groups(self._global_admin).get(self._local_group)
        self._global_admin.get_multi.assert_called_once_with(f'/localGroups/{self._groupname}', mock.ANY)
        expected_include = ['/' + attr for attr in groups.Groups.default]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual('Could not find group', error.exception.message)

    def _get_group_object(self, **kwargs):
        group_object = Object()
        group_object._classname = self._group_class_name  # pylint: disable=protected-access
        for key, value in kwargs.items():
            setattr(group_object, key, value)
        return group_object

    def test_list_local_groups_default_attrs(self):
        with mock.patch("cterasdk.core.groups.query.iterator") as query_iterator_mock:
            groups.Groups(self._global_admin).list_local_groups()
            query_iterator_mock.assert_called_once_with(self._global_admin, '/localGroups', mock.ANY)
            expected_query_params = base_core.BaseCoreTest._create_query_params(include=groups.Groups.default,
                                                                                start_from=0, count_limit=50)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_list_domain_groups_default_attrs(self):
        with mock.patch("cterasdk.core.groups.query.iterator") as query_iterator_mock:
            groups.Groups(self._global_admin).list_domain_groups()
            query_iterator_mock.assert_called_once_with(self._global_admin, f'/domains/{self._domain}/adGroups', mock.ANY)
            expected_query_params = base_core.BaseCoreTest._create_query_params(include=groups.Groups.default,
                                                                                start_from=0, count_limit=50)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_add_local_group(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = groups.Groups(self._global_admin).add(self._groupname, self._description)
        self._global_admin.execute.assert_called_once_with('', 'addGroup', mock.ANY)
        expected_param = self._get_add_group_object(name=self._groupname, description=self._description)
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def _get_add_group_object(self, **kwargs):
        param = Object()
        param._classname = 'AddGroupParam'  # pylint: disable=protected-access
        param.groupData = self._get_group_object(**kwargs)
        return param

    def test_delete_group(self):
        execute_response = 'Success'
        for group_account in [self._local_group, self._domain_group]:
            self._init_global_admin(execute_response=delete_response)
            ret = groups.Groups(self._global_admin).delete(group_account)
            self.assertEqual(ret, delete_response)
        self._global_admin.execute.assert_has_calls(
            [
                mock.call(f'/localGroups/{self._groupname}', 'delete', True),
                mock.call(f'/domains/{self._domain}/adGroups/{self._groupname}', 'delete', True)
            ]
        )
