from unittest import mock

from cterasdk import exception
from cterasdk.core import cloudfs
from cterasdk.core.types import UserAccount
from cterasdk.core import query, union
from cterasdk.common import Object
from tests.ut import base_core


class TestCoreCloudFS(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._owner = 'admin'
        self._local_user_account = UserAccount(self._owner)
        self._group = 'admin'
        self._name = 'folderGroup'
        self._user_uid = 1337

    def test_list_folder_groups_owned_by(self):
        get_user_uid_mock = self._mock_get_user_uid()
        with mock.patch("cterasdk.core.devices.query.iterator") as query_iterator_mock:
            cloudfs.CloudFS(self._global_admin).list_folder_groups(user=self._local_user_account)
            get_user_uid_mock.assert_called_once_with(self._local_user_account, ['uid'])
            query_iterator_mock.assert_called_once_with(self._global_admin, '/foldersGroups', mock.ANY)
            expected_param = TestCoreCloudFS._get_list_folder_groups_param(user_uid=self._user_uid)
            actual_param = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_list_folder_groups_param(include=None, user_uid=None):
        include = union.union(include or [], ['name', 'owner'])
        builder = query.QueryParamBuilder().include(include)
        if user_uid:
            builder.ownedBy(user_uid)
        return builder.build()

    def _mock_get_user_uid(self):
        param = Object()
        param.uid = self._user_uid
        get_user_uid_mock = self.patch_call("cterasdk.core.users.Users.get")
        get_user_uid_mock.return_value = param
        return get_user_uid_mock

    def test_mkfg_no_owner(self):
        self._init_global_admin(execute_response='Success')
        ret = cloudfs.CloudFS(self._global_admin).mkfg(self._name)

        self._global_admin.get.assert_not_called()
        self._global_admin.execute.assert_called_once_with('', 'createFolderGroup', mock.ANY)

        expected_param = self._get_mkfg_object()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, 'Success')

    def test_mkfg_with_local_owner(self):
        self._init_global_admin(execute_response='Success')
        self._mock_get_user_base_object_ref()

        ret = cloudfs.CloudFS(self._global_admin).mkfg(self._name, user=self._local_user_account)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.execute.assert_called_once_with('', 'createFolderGroup', mock.ANY)

        expected_param = self._get_mkfg_object(with_owner=True)
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

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

    def test_list_folders_owned_by(self):
        get_user_uid_mock = self._mock_get_user_uid()
        with mock.patch("cterasdk.core.devices.query.iterator") as query_iterator_mock:
            cloudfs.CloudFS(self._global_admin).list_folders(user=self._local_user_account)
            get_user_uid_mock.assert_called_once_with(self._local_user_account, ['uid'])
            query_iterator_mock.assert_called_once_with(self._global_admin, '/cloudDrives', mock.ANY)
            expected_param = TestCoreCloudFS._get_list_folders_param(user_uid=self._user_uid)
            actual_param = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_list_folders_param(include=None, deleted=False, user_uid=None):
        include = union.union(include or [], cloudfs.CloudFS.default)
        builder = query.QueryParamBuilder().include(include)
        query_filter = query.FilterBuilder('isDeleted').eq(deleted)
        builder.addFilter(query_filter)
        if user_uid:
            builder.ownedBy(user_uid)
        return builder.build()

    def test_mkdir_with_local_owner_no_winacls_param(self):
        self._init_global_admin(get_response='admin', execute_response='Success')
        self._mock_get_user_base_object_ref()

        ret = cloudfs.CloudFS(self._global_admin).mkdir(self._name, self._group, self._local_user_account)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.get.assert_called_once_with('/foldersGroups/' + self._group + '/baseObjectRef')
        self._global_admin.execute.assert_called_once_with('', 'addCloudDrive', mock.ANY)

        expected_param = self._get_mkdir_object()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

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
        self._assert_equal_objects(actual_param, expected_param)

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
        self._assert_equal_objects(actual_param, expected_param)

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
