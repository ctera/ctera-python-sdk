from unittest import mock

from cterasdk import exceptions
from cterasdk.edge import users
from cterasdk.common import Object
from tests.ut.edge import base_edge


class TestEdgeUsers(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._username = 'alice'
        self._password = 'W!zardOf0z'
        self._full_name = 'Alice Wonderland'
        self._uid = 516
        self._email = 'alice.wonderland@microsoft.com'
        self._login_mock = self.patch_call('cterasdk.objects.synchronous.edge.Edge.login')

    def test_get_all_users(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = users.Users(self._filer).get()
        self._filer.api.get.assert_called_once_with('/config/auth/users')
        self.assertEqual(ret, get_response)

    def test_get_user(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = users.Users(self._filer).get(self._username)
        self._filer.api.get.assert_called_once_with('/config/auth/users/' + self._username)
        self.assertEqual(ret, get_response)

    def test_add_first_user(self):
        info = Object()
        info.isfirstlogin = True
        self._init_filer(get_response=info)

        users.Users(self._filer).add_first_user(self._username, self._password)
        self._filer.api.get.assert_called_once_with('/nosession/logininfo')
        self._filer.api.post.assert_called_once_with('/nosession/createfirstuser', mock.ANY)

        expected_param = self._get_first_user_object('')
        actual_param = self._filer.api.post.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self._login_mock.assert_called_once_with(self._username, self._password)

    def test_add_first_user_with_email(self):
        info = Object()
        info.isfirstlogin = True
        self._init_filer(get_response=info)

        users.Users(self._filer).add_first_user(self._username, self._password, self._email)
        self._filer.api.get.assert_called_once_with('/nosession/logininfo')
        self._filer.api.post.assert_called_once_with('/nosession/createfirstuser', mock.ANY)

        expected_param = self._get_first_user_object(self._email)
        actual_param = self._filer.api.post.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self._login_mock.assert_called_once_with(self._username, self._password)

    def test_first_user_already_exists(self):
        info = Object()
        info.isfirstlogin = False
        self._init_filer(get_response=info)

        users.Users(self._filer).add_first_user(self._username, self._password)
        self._filer.api.get.assert_called_once_with('/nosession/logininfo')
        self._filer.api.post.assert_not_called()
        self._login_mock.assert_called_once_with(self._username, self._password)

    def test_add_user(self):
        add_response = '/config/auth/users/' + self._username
        self._init_filer(add_response=add_response)

        ret = users.Users(self._filer).add(self._username, self._password)
        self._filer.api.add.assert_called_once_with('/config/auth/users', mock.ANY)

        expected_param = self._get_user_object()
        actual_param = self._filer.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, add_response)

    def test_add_user_raise(self):
        expected_exception = exceptions.CTERAException()
        self._filer.api.add = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            users.Users(self._filer).add(self._username, self._password)
        self.assertEqual(f'User creation failed: {self._username}', str(error.exception))

    def test_modify_user(self):
        get_response = Object()
        get_response.username = self._username
        put_response = 'Success'
        self._init_filer(get_response=get_response, put_response=put_response)
        ret = users.Users(self._filer).modify(self._username, self._password, self._full_name, self._email, self._uid)

        self._filer.api.get.assert_called_once_with('/config/auth/users/' + self._username)
        self._filer.api.put.assert_called_once_with('/config/auth/users/' + self._username, mock.ANY)
        expected_param = self._get_user_object(self._full_name, self._email, self._uid)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, put_response)

    def test_modify_user_not_found(self):
        ref = f'/config/auth/users/{self._username}'
        self._filer.api.get = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            users.Users(self._filer).modify(self._username)
        self._filer.api.get.assert_called_once_with(ref)
        self.assertEqual(f'User not found: {ref}', str(error.exception))

    def test_modify_user_update_failed(self):
        get_response = Object()
        get_response.username = self._username
        self._init_filer(get_response=get_response)
        self._filer.api.put = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            users.Users(self._filer).modify(self._username, self._password, self._full_name, self._email, self._uid)

        ref = f'/config/auth/users/{self._username}'
        self._filer.api.get.assert_called_once_with(ref)
        self._filer.api.put.assert_called_once_with('/config/auth/users/' + self._username, mock.ANY)
        expected_param = self._get_user_object(self._full_name, self._email, self._uid)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(f'User modification failed: {ref}', str(error.exception))

    def test_delete_user(self):
        user = self._get_user_object()
        self._init_filer(delete_response=user)

        ret = users.Users(self._filer).delete(self._username)
        self._filer.api.delete.assert_called_once_with('/config/auth/users/' + self._username)

        self.assertEqual(user.username, ret.username)

    def test_delete_user_raise(self):
        expected_exception = exceptions.CTERAException()
        self._filer.api.delete = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            users.Users(self._filer).delete(self._username)
        self.assertEqual(f'User deletion failed: /config/auth/users/{self._username}', str(error.exception))

    def _get_user_object(self, full_name=None, email=None, uid=None):
        o = Object()
        o.username = self._username
        o.password = self._password
        o.fullName = full_name
        o.email = email
        o.uid = uid
        return o

    def _get_first_user_object(self, email):
        o = Object()
        o.username = self._username
        o.password = self._password
        o.email = email
        return o
