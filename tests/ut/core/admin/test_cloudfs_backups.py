from unittest import mock
import munch

from cterasdk import exceptions
from cterasdk.core import cloudfs
from cterasdk.core.types import UserAccount
from tests.ut.core.admin import base_admin


class TestCoreBackups(base_admin.BaseCoreTest):   # pylint: disable=too-many-public-methods

    # pylint: disable=too-many-instance-attributes
    def setUp(self):
        super().setUp()
        self._username = 'user'
        self._owner = UserAccount(self._username)
        self._new_owner = UserAccount('user2')
        self._new_owner_ref = 'objs/new_owner/10'
        self._group = 'folder-group'
        self._new_group = 'folder-group'
        self._new_group_ref = 'objs/new_group/11'
        self._name = 'backup-folder'
        self._new_name = 'renamed-backup-folder'
        self._user_uid = 1500
        self._user_ref = 'objs/36'
        self._mock_get_user_ref = self.patch_call("cterasdk.core.users.Users.get")
        self._mock_get_user_ref.return_value = munch.Munch({'baseObjectRef': self._user_ref})
        self._group_ref = 'objs/51'
        self._mock_get_group_ref = self.patch_call("cterasdk.core.cloudfs.FolderGroups.get")
        self._mock_get_group_ref.return_value = munch.Munch({'baseObjectRef': self._group_ref})

    def test_add_backup_folder_success(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = cloudfs.Backups(self._global_admin).add(self._name, self._group, self._owner)
        self._mock_get_user_ref.assert_called_once_with(self._owner, ['baseObjectRef'])
        self._mock_get_group_ref.assert_called_once_with(self._group, ['baseObjectRef'])
        self._global_admin.api.add.assert_called_once_with('/backups', mock.ANY)
        expected_param = TestCoreBackups._get_backup_folder_object(self._name, self._group_ref, self._user_ref, True)
        actual_param = self._global_admin.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_add_backup_folder_failure(self):
        error_message = "Expected Failure"
        expected_exception = exceptions.CTERAException(message=error_message)
        self._global_admin.api.add = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            cloudfs.Backups(self._global_admin).add(self._name, self._group, self._owner)
        self._mock_get_user_ref.assert_called_once_with(self._owner, ['baseObjectRef'])
        self._mock_get_group_ref.assert_called_once_with(self._group, ['baseObjectRef'])
        self._global_admin.api.add.assert_called_once_with('/backups', mock.ANY)
        expected_param = TestCoreBackups._get_backup_folder_object(self._name, self._group_ref, self._user_ref, True)
        actual_param = self._global_admin.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(error_message, error.exception.message)

    def test_modify_backup_folder_success(self):
        put_response = 'Success'
        self._mock_get_user_ref.return_value = munch.Munch({'baseObjectRef': self._new_owner_ref})
        self._mock_get_group_ref.return_value = munch.Munch({'baseObjectRef': self._new_group_ref})
        get_response = TestCoreBackups._get_backup_folder_object(self._name, self._group_ref, self._user_ref, True)
        self._init_global_admin(get_response=get_response, put_response=put_response)
        ret = cloudfs.Backups(self._global_admin).modify(self._name, self._new_name, self._new_owner, self._new_group, False)
        self._mock_get_user_ref.assert_called_once_with(self._new_owner, ['baseObjectRef'])
        self._mock_get_group_ref.assert_called_once_with(self._new_group, include=['baseObjectRef'])
        self._global_admin.api.get.assert_called_once_with(f'/backups/{self._name}')
        self._global_admin.api.put.assert_called_once_with(f'/backups/{self._name}', mock.ANY)
        expected_param = TestCoreBackups._get_backup_folder_object(self._new_name, self._new_group_ref, self._new_owner_ref, True)
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_delete_backup_folder(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = cloudfs.Backups(self._global_admin).delete(self._name)
        self._global_admin.api.execute.assert_called_once_with(f'/backups/{self._name}', 'delete')
        self.assertEqual(ret, execute_response)

    @staticmethod
    def _get_backup_folder_object(name, group_ref, user_ref, xattr):
        param = munch.Munch()
        param._classname = 'Backup'  # pylint: disable=protected-access
        param.name = name
        param.group = group_ref
        param.owner = user_ref
        param.enableBackupExtendedAttributes = xattr
        return param
