from unittest import mock
import munch

from cterasdk import exceptions, core_enum
from cterasdk.core import cloudfs
from cterasdk.core.types import UserAccount
from cterasdk.core import query
from cterasdk.common import Object, union
from tests.ut import base_core


class TestCoreFolderGroups(base_core.BaseCoreTest):   # pylint: disable=too-many-public-methods

    def setUp(self):
        super().setUp()
        self._owner = 'admin'
        self._local_user_account = UserAccount(self._owner)
        self._name = 'folderGroup'
        self._new_name = 'folderGroup2'
        self._user_uid = 1337
        self.fixed_block_size = core_enum.DeduplicationMethodType.FixedBlockSize

    def test_list_folder_groups_owned_by(self):
        get_user_uid_mock = self._mock_get_user_uid()
        with mock.patch("cterasdk.core.devices.query.iterator") as query_iterator_mock:
            cloudfs.FolderGroups(self._global_admin).all(user=self._local_user_account)
            get_user_uid_mock.assert_called_once_with(self._local_user_account, ['uid'])
            query_iterator_mock.assert_called_once_with(self._global_admin, '/foldersGroups', mock.ANY)
            expected_param = TestCoreFolderGroups._get_list_folder_groups_param(user_uid=self._user_uid)
            actual_param = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_list_folder_groups_param(include=None, user_uid=None):
        include = union(include or [], ['name', 'owner'])
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

    def test_add_folder_group_no_owner(self):
        self._init_global_admin(execute_response='Success')
        ret = cloudfs.FolderGroups(self._global_admin).add(self._name)

        self._global_admin.api.get.assert_not_called()
        self._global_admin.api.execute.assert_called_once_with('', 'createFolderGroup', mock.ANY)

        expected_param = self._get_add_folder_group_object()
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, 'Success')

    def test_add_folder_group_with_local_owner(self):
        self._init_global_admin(execute_response='Success')
        self._mock_get_user_base_object_ref()

        ret = cloudfs.CloudFS(self._global_admin).groups.add(self._name, user=self._local_user_account)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.api.execute.assert_called_once_with('', 'createFolderGroup', mock.ANY)

        expected_param = self._get_add_folder_group_object(with_owner=True)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, 'Success')

    def test_add_folder_group_no_owner_raise(self):
        error_message = "Expected Failure"
        expected_exception = exceptions.CTERAException(message=error_message)
        self._global_admin.api.execute = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            cloudfs.FolderGroups(self._global_admin).add(self._name)
        self.assertEqual(error_message, error.exception.message)

    def test_add_folder_group_no_owner_fixed_block_size(self):
        self._init_global_admin(execute_response='Success')
        ret = cloudfs.FolderGroups(self._global_admin).add(self._name, deduplication_method_type=self.fixed_block_size)
        self._global_admin.api.get.assert_not_called()
        self._global_admin.api.execute.assert_called_once_with('', 'createFolderGroup', mock.ANY)
        expected_param = self._get_add_folder_group_object(fixed_block_size=True)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, 'Success')

    def test_add_folder_group_with_local_owner_fixed_block_size(self):
        self._init_global_admin(execute_response='Success')
        self._mock_get_user_base_object_ref()
        ret = cloudfs.FolderGroups(self._global_admin).add(self._name, user=self._local_user_account,
                                                           deduplication_method_type=self.fixed_block_size)
        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.api.execute.assert_called_once_with('', 'createFolderGroup', mock.ANY)
        expected_param = self._get_add_folder_group_object(with_owner=True, fixed_block_size=True)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, 'Success')

    def test_add_folder_group_no_owner_raise_fixed_block_size(self):
        error_message = "Expected Failure"
        expected_exception = exceptions.CTERAException(message=error_message)
        self._global_admin.api.execute = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            cloudfs.FolderGroups(self._global_admin).add(self._name, deduplication_method_type=self.fixed_block_size)
        self.assertEqual(error_message, error.exception.message)

    def test_modify_folder_group(self):
        get_response = munch.Munch(dict(name=self._name))
        self._init_global_admin(get_response=get_response, put_response='Success')
        ret = cloudfs.FolderGroups(self._global_admin).modify(self._name, self._new_name)
        self._global_admin.api.get.assert_called_once_with(f'/foldersGroups/{self._name}')
        self._global_admin.api.put.assert_called_once_with(f'/foldersGroups/{self._name}', mock.ANY)
        expected_param = munch.Munch(dict(name=self._new_name))
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, 'Success')

    def test_modify_folder_group_user_not_exists(self):
        error_message = "Failed to get folder group"
        expected_exception = exceptions.CTERAException(message=error_message)
        self._global_admin.api.get = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            cloudfs.FolderGroups(self._global_admin).modify(self._name, self._new_name)
        self.assertEqual(error_message, error.exception.message)

    def test_modify_folder_group_update_failure(self):
        error_message = "Expected Failure"
        expected_exception = exceptions.CTERAException(message=error_message)
        self._global_admin.api.get = mock.MagicMock(return_value=munch.Munch(dict(name=self._name)))
        self._global_admin.api.put = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            cloudfs.FolderGroups(self._global_admin).modify(self._name, self._new_name)
        self.assertEqual(error_message, error.exception.message)

    def test_delete(self):
        self._init_global_admin(execute_response='Success')
        cloudfs.FolderGroups(self._global_admin).delete(self._name)
        self._global_admin.api.execute.assert_called_once_with('/foldersGroups/' + self._name, 'deleteGroup', True)

    def _get_add_folder_group_object(self, with_owner=False, fixed_block_size=False):
        add_folder_group_param = Object()
        add_folder_group_param.name = self._name
        add_folder_group_param.disabled = False
        add_folder_group_param.owner = self._owner if with_owner else None
        add_folder_group_param.deduplicationMethodType = self.fixed_block_size if fixed_block_size else None
        return add_folder_group_param

    def _get_user_object(self, **kwargs):
        user_account = Object()
        user_account.name = self._owner
        for key, value in kwargs.items():
            setattr(user_account, key, value)
        return user_account

    def _mock_get_user_base_object_ref(self):
        user_object = self._get_user_object(baseObjectRef=self._owner)
        self._mock_get_user(user_object)

    def _mock_get_user(self, return_value):
        self._global_admin.users.get = mock.MagicMock(return_value=return_value)
