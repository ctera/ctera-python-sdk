from unittest import mock

from cterasdk import exception
from cterasdk.common import Object
from cterasdk.core.types import UserAccount
from cterasdk.core import users
from tests.ut import base_core


class TestCoreUsers(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._user_class_name = 'PortalUser'
        self._username = 'alice'
        self._user_account = UserAccount(self._username)
        self._email = 'alice@wonderland.com'
        self._first_name = 'Alice'
        self._last_name = 'Wonderland'
        self._password = 'password'
        self._role = 'EndUser'
        self._domain = 'ctera.local'
        self._domains = ['na.ctera.local', 'eu.ctera.local']

    def test_get_user_default_attrs(self):
        get_multi_response = self._get_user_object(name=self._user_account.name)
        self._init_global_admin(get_multi_response=get_multi_response)
        ret = users.Users(self._global_admin).get(self._user_account)
        self._global_admin.get_multi.assert_called_once_with('/users/' + self._user_account.name, mock.ANY)
        expected_include = ['/' + attr for attr in users.Users.default]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual(ret.name, self._user_account.name)

    def test_add_user_required_args(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = users.Users(self._global_admin).add(self._username, self._email, self._first_name,
                                                  self._last_name, self._password, self._role)
        self._global_admin.add.assert_called_once_with('/users', mock.ANY)
        expected_param = self._get_user_object(name=self._username, email=self._email, firstName=self._first_name,
                                               lastName=self._last_name, password=self._password,
                                               role=self._role, company=None, comment=None)
        actual_param = self._global_admin.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_list_local_users_default_attrs(self):
        with mock.patch("cterasdk.core.users.query.iterator") as query_iterator_mock:
            users.Users(self._global_admin).list_local_users()
            query_iterator_mock.assert_called_once_with(self._global_admin, '/users', mock.ANY)
            expected_query_params = base_core.BaseCoreTest._create_query_params(include=users.Users.default, start_from=0, count_limit=50)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_list_domain_users_default_attrs(self):
        with mock.patch("cterasdk.core.users.query.iterator") as query_iterator_mock:
            users.Users(self._global_admin).list_domain_users(self._domain)
            query_iterator_mock.assert_called_once_with(self._global_admin, '/domains/' + self._domain + '/adUsers', mock.ANY)
            expected_query_params = base_core.BaseCoreTest._create_query_params(include=users.Users.default, start_from=0, count_limit=50)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_list_domains(self):
        get_response = self._domains
        self._init_global_admin(get_response=get_response)
        ret = users.Users(self._global_admin).list_domains()
        self._global_admin.get.assert_called_once_with('/domains')
        self.assertEqual(ret, get_response)

    def test_get_user_not_found(self):
        get_multi_response = self._get_user_object(name=None)
        self._init_global_admin(get_multi_response=get_multi_response)
        with self.assertRaises(exception.CTERAException) as error:
            users.Users(self._global_admin).get(self._user_account)
        self._global_admin.get_multi.assert_called_once_with('/users/' + self._user_account.name, mock.ANY)
        expected_include = ['/' + attr for attr in users.Users.default]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual('Could not find user', error.exception.message)

    def test_delete_user(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = users.Users(self._global_admin).delete(self._username)
        self._global_admin.execute.assert_called_once_with('/users/' + self._username, 'delete', True)
        self.assertEqual(ret, execute_response)

    def _get_user_object(self, **kwargs):
        user_object = Object()
        user_object._classname = self._user_class_name  # pylint: disable=protected-access
        for key, value in kwargs.items():
            setattr(user_object, key, value)
        return user_object
