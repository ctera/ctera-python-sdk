from unittest import mock
import munch

from cterasdk import exceptions
from cterasdk.core import cloudfs
from cterasdk.core.types import UserAccount, ComplianceSettingsBuilder, ExtendedAttributesBuilder
from cterasdk.core import query
from cterasdk.common import Object, union
from tests.ut import base_core


class TestCoreCloudDrives(base_core.BaseCoreTest):   # pylint: disable=too-many-public-methods, too-many-instance-attributes

    def setUp(self):
        super().setUp()
        self._owner = 'admin'
        self._cloudfolder_name = 'folder_name'
        self._cloudfolder_baseObjecrRef = 'objs/1'
        self._local_user_account = UserAccount(self._owner)
        self._group = 'admin'
        self._name = 'folderGroup'
        self._description = 'description'
        self._user_uid = 1337
        self._folder_uid = 7331

        self._nt_acl_folders = Object()
        self._nt_acl_folders._classname = 'SDDLFoldersParam'  # pylint: disable=protected-access
        self._nt_acl_folders.foldersPath = ["testfolder/sadada", "testfolder1/one"]
        self._nt_acl_folders.sddlString = 'O:S-1-12-1-1536910496-1126310805-1188065941-1612002142' \
                                          'G:S-1-12-1-1536910496-1126310805-1188065941-1612002142' \
                                          'D:AI(A;ID;FA;;;BA)(A;ID;FA;;;SY)(A;ID;0x1200a9;;;BU)(A;ID;0x1301bf;;;AU)'
        self._nt_acl_folders.isRecursive = True

        self._nt_acl_owner = Object()
        self._nt_acl_owner._classname = 'SDDLFoldersParam'  # pylint: disable=protected-access
        self._nt_acl_owner.foldersPath = ["testfolder/sadada", "testfolder1/one"]
        self._nt_acl_owner.ownerSid = 'S-1-12-1-1536910496-1126310805-1188065941-1612002142'
        self._nt_acl_owner.isRecursive = True

    def test_list_folders_owned_by(self):
        get_user_uid_mock = self._mock_get_user_uid()
        with mock.patch("cterasdk.core.devices.query.iterator") as query_iterator_mock:
            cloudfs.CloudDrives(self._global_admin).all(user=self._local_user_account)
            get_user_uid_mock.assert_called_once_with(self._local_user_account, ['uid'])
            query_iterator_mock.assert_called_once_with(self._global_admin, '/cloudDrives', mock.ANY)
            expected_param = TestCoreCloudDrives._get_list_folders_param(user_uid=self._user_uid)
            actual_param = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_list_folders_param(include=None, include_deleted=False, filter_deleted=False, user_uid=None):
        include = union(include or [], cloudfs.CloudDrives.default)
        builder = query.QueryParamBuilder().include(include)
        if include_deleted:
            builder.put('includeDeleted', True)
        if filter_deleted:
            query_filter = query.FilterBuilder('isDeleted').eq(True)
            builder.addFilter(query_filter)
        if user_uid:
            builder.ownedBy(user_uid)
        return builder.build()

    def test_add_cloud_drive_with_local_owner_no_winacls_param(self):
        self._init_global_admin(get_response='admin', execute_response='Success')
        self._mock_get_user_base_object_ref()
        self._mock_get_folder_group()

        ret = cloudfs.CloudDrives(self._global_admin).add(self._name, self._group, self._local_user_account)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.cloudfs.groups.get.assert_called_once_with(self._group, ['baseObjectRef'])
        self._global_admin.api.execute.assert_called_once_with('', 'addCloudDrive', mock.ANY)

        expected_param = self._get_add_cloud_drive_object()
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, 'Success')

    def test_add_cloud_drive_with_local_owner_no_winacls_param_with_description(self):
        self._init_global_admin(get_response='admin', execute_response='Success')
        self._mock_get_user_base_object_ref()
        self._mock_get_folder_group()

        ret = cloudfs.CloudDrives(self._global_admin).add(self._name, self._group, self._local_user_account, description=self._description)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.cloudfs.groups.get.assert_called_once_with(self._group, ['baseObjectRef'])
        self._global_admin.api.execute.assert_called_once_with('', 'addCloudDrive', mock.ANY)

        expected_param = self._get_add_cloud_drive_object(description=self._description)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, 'Success')

    def test_add_cloud_drive_with_local_owner_winacls_true(self):
        get_response = 'admin'
        self._init_global_admin(get_response=get_response, execute_response='Success')
        self._mock_get_user_base_object_ref()
        self._mock_get_folder_group()

        ret = cloudfs.CloudDrives(self._global_admin).add(self._name, self._group, self._local_user_account, True)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.cloudfs.groups.get.assert_called_once_with(self._group, ['baseObjectRef'])
        self._global_admin.api.execute.assert_called_once_with('', 'addCloudDrive', mock.ANY)

        expected_param = self._get_add_cloud_drive_object()
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, 'Success')

    def test_add_cloud_drive_with_local_owner_winacls_false(self):
        get_response = 'admin'
        self._init_global_admin(get_response=get_response, execute_response='Success')
        self._mock_get_user_base_object_ref()
        self._mock_get_folder_group()

        ret = cloudfs.CloudDrives(self._global_admin).add(self._name, self._group, self._local_user_account, False,
                                                          xattrs=ExtendedAttributesBuilder.disabled().build())

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.cloudfs.groups.get.assert_called_once_with(self._group, ['baseObjectRef'])
        self._global_admin.api.execute.assert_called_once_with('', 'addCloudDrive', mock.ANY)

        expected_param = self._get_add_cloud_drive_object(winacls=False)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, 'Success')

    def test_add_cloud_drive_with_local_owner_raise(self):
        get_response = 'admin'
        self._init_global_admin(get_response=get_response, execute_response='Success')
        self._mock_get_user_base_object_ref()
        self._mock_get_folder_group()

        error_message = "Expected Failure"
        expected_exception = exceptions.CTERAException(message=error_message)
        self._global_admin.api.execute = mock.MagicMock(side_effect=expected_exception)
        with self.assertRaises(exceptions.CTERAException) as error:
            cloudfs.CloudDrives(self._global_admin).add(self._name, self._group, self._local_user_account)

        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['baseObjectRef'])
        self._global_admin.cloudfs.groups.get.assert_called_once_with(self._group, ['baseObjectRef'])

        self.assertEqual(error_message, error.exception.message)

    def test_delete_with_local_owner(self):
        self._init_global_admin()
        with mock.patch("cterasdk.core.cloudfs.query.iterator") as query_iterator_mock:
            query_iterator_mock.return_value = iter([munch.Munch({'uid': self._folder_uid, 'isDeleted': False})])
            cloudfs.CloudDrives(self._global_admin).delete(self._name, self._local_user_account)
            query_iterator_mock.assert_called_once_with(self._global_admin, '/cloudDrives', mock.ANY)
            self._global_admin.api.execute.assert_called_once_with(f'/objs/{self._folder_uid}', 'delete')

    def test_delete_permanently_with_local_owner(self):
        self._init_global_admin()
        with mock.patch("cterasdk.core.cloudfs.query.iterator") as query_iterator_mock:
            query_iterator_mock.return_value = iter([munch.Munch({'uid': self._folder_uid, 'isDeleted': True})])
            cloudfs.CloudDrives(self._global_admin).delete(self._name, self._local_user_account, permanently=True)
            query_iterator_mock.assert_called_once_with(self._global_admin, '/cloudDrives', mock.ANY)
            self._global_admin.api.execute.assert_called_once_with(f'/objs/{self._folder_uid}', 'deleteFolderPermanently')

    def test_undelete_with_local_owner(self):
        self._init_global_admin(get_response=self._owner)
        self._mock_get_user_display_name()
        self._global_admin.files.undelete = mock.MagicMock(return_value='Success')
        cloudfs.CloudDrives(self._global_admin).recover(self._name, self._local_user_account)
        self._global_admin.users.get.assert_called_once_with(self._local_user_account, ['displayName'])
        self._global_admin.files.undelete.assert_called_once_with(f'Users/{self._owner}/{self._name}')

    def _get_add_cloud_drive_object(self, winacls=True, description=None, quota=None, compliance_settings=None, xattrs=None):
        add_cloud_drive_param = Object()
        add_cloud_drive_param.name = self._name
        add_cloud_drive_param.owner = self._owner
        add_cloud_drive_param.group = self._group
        add_cloud_drive_param.enableSyncWinNtExtendedAttributes = winacls
        add_cloud_drive_param.folderQuota = quota
        if description:
            add_cloud_drive_param.description = description
        add_cloud_drive_param.wormSettings = compliance_settings if compliance_settings else ComplianceSettingsBuilder.default().build()
        add_cloud_drive_param.extendedAttributes = xattrs if xattrs else ExtendedAttributesBuilder.default().build()
        return add_cloud_drive_param

    def _mock_get_user_base_object_ref(self):
        user_object = self._get_user_object(baseObjectRef=self._owner)
        self._mock_get_user(user_object)

    def _mock_get_user_display_name(self):
        user_object = self._get_user_object(displayName=self._owner)
        self._mock_get_user(user_object)

    def _mock_get_user(self, return_value):
        self._global_admin.users.get = mock.MagicMock(return_value=return_value)

    def _mock_get_folder_group(self):
        self._global_admin.cloudfs.groups.get = mock.MagicMock(return_value=munch.Munch(dict(name=self._group, baseObjectRef=self._group)))

    def _mock_get_user_uid(self):
        param = Object()
        param.uid = self._user_uid
        get_user_uid_mock = self.patch_call("cterasdk.core.users.Users.get")
        get_user_uid_mock.return_value = param
        return get_user_uid_mock

    def _get_user_object(self, **kwargs):
        user_account = Object()
        user_account.name = self._owner
        for key, value in kwargs.items():
            setattr(user_account, key, value)
        return user_account

    def test_set_folders_acl_success(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = cloudfs.CloudDrives(self._global_admin).setfacl(self._nt_acl_folders.foldersPath, self._nt_acl_folders.sddlString,
                                                              self._nt_acl_folders.isRecursive)
        self._global_admin.api.execute.assert_called_once_with('', 'setFoldersACL', mock.ANY)
        self.assertEqual(ret, execute_response)

    def test_set_folders_acl_raise(self):
        expected_exception = exceptions.CTERAException()
        self._init_global_admin(execute_response=expected_exception)
        self._global_admin.api.execute = mock.MagicMock(side_effect=expected_exception)

        with self.assertRaises(exceptions.CTERAException) as error:
            cloudfs.CloudDrives(self._global_admin).setfacl(self._nt_acl_folders.foldersPath, self._nt_acl_folders.sddlString,
                                                            self._nt_acl_folders.isRecursive)
        self.assertEqual('Failed to setFoldersACL', error.exception.message)

    def test_set_owner_acl_success(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = cloudfs.CloudDrives(self._global_admin).setoacl(self._nt_acl_owner.foldersPath, self._nt_acl_owner.ownerSid,
                                                              self._nt_acl_owner.isRecursive)
        self._global_admin.api.execute.assert_called_once_with('', 'setOwnerACL', mock.ANY)
        self.assertEqual(ret, execute_response)

    def test_set_owner_acl_raise(self):
        expected_exception = exceptions.CTERAException()
        self._init_global_admin(execute_response=expected_exception)
        self._global_admin.api.execute = mock.MagicMock(side_effect=expected_exception)

        with self.assertRaises(exceptions.CTERAException) as error:
            cloudfs.CloudDrives(self._global_admin).setoacl(self._nt_acl_owner.foldersPath, self._nt_acl_owner.ownerSid,
                                                            self._nt_acl_owner.isRecursive)
        self.assertEqual('Failed to setOwnerACL', error.exception.message)

    def test_modify_cloudfolder_failure(self):
        mock_find_cloudfolder = self.patch_call('cterasdk.core.cloudfs.CloudDrives.find')
        mock_find_cloudfolder.return_value = munch.Munch({'baseObjectRef': self._cloudfolder_baseObjecrRef})
        self._init_global_admin(get_response=munch.Munch({'baseObjectRef': self._cloudfolder_baseObjecrRef}))
        self._global_admin.api.put = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException):
            cloudfs.CloudDrives(self._global_admin).modify(self._cloudfolder_name, self._local_user_account)
        self._global_admin.api.get.assert_called_once_with(self._cloudfolder_baseObjecrRef)
        self._global_admin.api.put.assert_called_once_with(f'/{self._cloudfolder_baseObjecrRef}', mock.ANY)
