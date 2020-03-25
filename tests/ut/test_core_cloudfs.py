from unittest import mock

from cterasdk import exception
from cterasdk.core import cloudfs
from cterasdk.core import types
from cterasdk.common import Object
from tests.ut import base_core


class TestCoreCloudFS(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._owner = 'admin'
        self._local_user_account = types.UserAccount(self._owner)
        self._group = 'admin'
        self._name = 'folderGroup'

    def test_mkfg_no_owner(self):
        self._init_global_admin(execute_response='Success')
        ret = cloudfs.CloudFS(self._global_admin).mkfg(self._name)

        self._global_admin.get.assert_not_called()
        self._global_admin.execute.assert_called_once_with('', 'createFolderGroup', mock.ANY)

        expected_param = self._get_mkfg_object()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual(ret, 'Success')

    def test_mkfg_with_local_owner(self):
        self._init_global_admin(execute_response='Success')
        self._mock_get_user_base_object_ref()

        ret = cloudfs.CloudFS(self._global_admin).mkfg(self._name, user=self._local_user_account)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.execute.assert_called_once_with('', 'createFolderGroup', mock.ANY)

        expected_param = self._get_mkfg_object(with_owner=True)
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual(ret, 'Success')

    def test_mkfg_no_owner_raise(self):
        error_message = "Expected Failure"
        expected_exception = exception.CTERAException(message=error_message)
        self._global_admin.execute = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            cloudfs.CloudFS(self._global_admin).mkfg(self._name)
        self.assertEqual(error_message, error.exception.message)

    def test_rmfg(self):
        self._init_global_admin(execute_response='Success')
        cloudfs.CloudFS(self._global_admin).rmfg(self._name)
        self._global_admin.execute.assert_called_once_with('/foldersGroups/' + self._name, 'deleteGroup', True)

    def test_mkdir_with_local_owner_no_winacls_param(self):
        self._init_global_admin(get_response='admin', execute_response='Success')
        self._mock_get_user_base_object_ref()

        ret = cloudfs.CloudFS(self._global_admin).mkdir(self._name, self._group, self._local_user_account)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.get.assert_called_once_with('/foldersGroups/' + self._group + '/baseObjectRef')
        self._global_admin.execute.assert_called_once_with('', 'addCloudDrive', mock.ANY)

        expected_param = self._get_mkdir_object()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual(ret, 'Success')

    def test_mkdir_with_local_owner_winacls_true(self):
        get_response = 'admin'
        self._init_global_admin(get_response=get_response, execute_response='Success')
        self._mock_get_user_base_object_ref()

        ret = cloudfs.CloudFS(self._global_admin).mkdir(self._name, self._group, self._local_user_account, True)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.get.assert_called_once_with('/foldersGroups/' + self._group + '/baseObjectRef')
        self._global_admin.execute.assert_called_once_with('', 'addCloudDrive', mock.ANY)

        expected_param = self._get_mkdir_object()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual(ret, 'Success')

    def test_mkdir_with_local_owner_winacls_false(self):
        get_response = 'admin'
        self._init_global_admin(get_response=get_response, execute_response='Success')
        self._mock_get_user_base_object_ref()

        ret = cloudfs.CloudFS(self._global_admin).mkdir(self._name, self._group, self._local_user_account, False)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.get.assert_called_once_with('/foldersGroups/' + self._group + '/baseObjectRef')
        self._global_admin.execute.assert_called_once_with('', 'addCloudDrive', mock.ANY)

        expected_param = self._get_mkdir_object(winacls=False)
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual(ret, 'Success')

    def test_mkdir_with_local_owner_raise(self):
        get_response = 'admin'
        self._init_global_admin(get_response=get_response, execute_response='Success')
        self._mock_get_user_base_object_ref()

        error_message = "Expected Failure"
        expected_exception = exception.CTERAException(message=error_message)
        self._global_admin.execute = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exception.CTERAException) as error:
            cloudfs.CloudFS(self._global_admin).mkdir(self._name, self._group, self._local_user_account)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.get.assert_called_once_with('/foldersGroups/' + self._group + '/baseObjectRef')

        self.assertEqual(error_message, error.exception.message)

    def test_delete_with_local_owner(self):
        self._init_global_admin(get_response=self._owner)
        self._mock_get_user_display_name()

        self._global_admin.files.delete = mock.MagicMock(return_value='Success')
        cloudfs.CloudFS(self._global_admin).delete(self._name, self._local_user_account)
        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['displayName'])
        self._global_admin.files.delete.assert_called_once_with(self._owner + '/' + self._name)

    def test_undelete_with_local_owner(self):
        self._init_global_admin(get_response=self._owner)
        self._mock_get_user_display_name()

        self._global_admin.files.undelete = mock.MagicMock(return_value='Success')
        cloudfs.CloudFS(self._global_admin).undelete(self._name, self._local_user_account)
        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['displayName'])
        self._global_admin.files.undelete.assert_called_once_with(self._owner + '/' + self._name)

    def _get_mkfg_object(self, with_owner=False):
        mkfg_param_object = Object()
        mkfg_param_object.name = self._name
        mkfg_param_object.disabled = True
        mkfg_param_object.owner = self._owner if with_owner else None
        return mkfg_param_object

    def _get_mkdir_object(self, winacls=True):
        mkdir_param_object = Object()
        mkdir_param_object.name = self._name
        mkdir_param_object.owner = self._owner
        mkdir_param_object.group = self._group
        mkdir_param_object.enableSyncWinNtExtendedAttributes = winacls
        return mkdir_param_object

    def _get_user_object(self, **kwargs):
        user_account = Object()
        user_account.name = self._owner
        for key, value in kwargs.items():
            setattr(user_account, key, value)
        return user_account

    def _mock_get_user_base_object_ref(self):
        user_object = self._get_user_object(baseObjectRef=self._owner)
        self._mock_get_user(user_object)

    def _mock_get_user_display_name(self):
        user_object = self._get_user_object(displayName=self._owner)
        self._mock_get_user(user_object)

    def _mock_get_user(self, return_value):
        self._global_admin.users.get = mock.MagicMock(return_value=return_value)
