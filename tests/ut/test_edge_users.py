from unittest import mock

from cterasdk import exception
from cterasdk.edge import users
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeUsers(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._username = 'alice'
        self._password = 'W!zardOf0z'
        self._email = 'alice.wonderland@microsoft.com'
        self._login_mock = self.patch_call("cterasdk.object.Gateway.login")

    def test_get_all_users(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = users.Users(self._filer).get()
        self._filer.get.assert_called_once_with('/config/auth/users')
        self.assertEqual(ret, get_response)

    def test_get_user(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = users.Users(self._filer).get(self._username)
        self._filer.get.assert_called_once_with('/config/auth/users/' + self._username)
        self.assertEqual(ret, get_response)

    def test_add_first_user(self):
        info = Object()
        info.isfirstlogin = True
        self._init_filer(get_response=info)

        users.Users(self._filer).add_first_user(self._username, self._password)
        self._filer.get.assert_called_once_with('/nosession/logininfo')
        self._filer.post.assert_called_once_with('/nosession/createfirstuser', mock.ANY)

        expected_param = self._get_first_user_object('')
        actual_param = self._filer.post.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)
        self._login_mock.assert_called_once_with(self._username, self._password)

    def test_add_first_user_with_email(self):
        info = Object()
        info.isfirstlogin = True
        self._init_filer(get_response=info)

        users.Users(self._filer).add_first_user(self._username, self._password, self._email)
        self._filer.get.assert_called_once_with('/nosession/logininfo')
        self._filer.post.assert_called_once_with('/nosession/createfirstuser', mock.ANY)

        expected_param = self._get_first_user_object(self._email)
        actual_param = self._filer.post.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)
        self._login_mock.assert_called_once_with(self._username, self._password)

    def test_first_user_already_exists(self):
        info = Object()
        info.isfirstlogin = False
        self._init_filer(get_response=info)

        users.Users(self._filer).add_first_user(self._username, self._password)
        self._filer.get.assert_called_once_with('/nosession/logininfo')
        self._filer.post.assert_not_called()
        self._login_mock.assert_called_once_with(self._username, self._password)

    def test_add_user(self):
        add_response = '/config/auth/users/' + self._username
        self._init_filer(add_response=add_response)

        ret = users.Users(self._filer).add(self._username, self._password)
        self._filer.add.assert_called_once_with('/config/auth/users', mock.ANY)

        expected_param = self._get_user_object()
        actual_param = self._filer.add.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual(ret, add_response)

    def test_add_user_raise(self):
        expected_exception = exception.CTERAException()
        self._filer.add = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            users.Users(self._filer).add(self._username, self._password)
        self.assertEqual('User creation failed', error.exception.message)

    def test_delete_user(self):
        user = self._get_user_object()
        self._init_filer(delete_response=user)

        ret = users.Users(self._filer).delete(self._username)
        self._filer.delete.assert_called_once_with('/config/auth/users/' + self._username)

        self.assertEqual(user.username, ret.username)

    def test_delete_user_raise(self):
        expected_exception = exception.CTERAException()
        self._filer.delete = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            users.Users(self._filer).delete(self._username)
        self.assertEqual('User deletion failed', error.exception.message)

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
