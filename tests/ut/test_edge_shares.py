from unittest import mock

from cterasdk import exception
from cterasdk.edge import shares
from cterasdk.edge.enum import Acl, ClientSideCaching, PrincipalType, FileAccessMode
from cterasdk.edge.types import ShareAccessControlEntry
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeShares(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._root = '/'
        self._share_name = 'Accounting'
        self._share_directory = 'users/Service Account/DATA/Accounting'
        self._share_volume = 'cloud'
        self._share_fullpath = '%s/%s' % (self._share_volume, self._share_directory)
        self._share_acl = [
            ShareAccessControlEntry(principal_type=PrincipalType.LG, name='Everyone', perm=FileAccessMode.RO),
            ShareAccessControlEntry(principal_type=PrincipalType.LU, name='admin', perm=FileAccessMode.RW),
            ShareAccessControlEntry(principal_type=PrincipalType.DG, name='CTERA\\Domain Admins', perm=FileAccessMode.RW),
            ShareAccessControlEntry(principal_type=PrincipalType.DU, name='walice@ctera.com', perm=FileAccessMode.RW)
        ]
        self._share_block_files = ['exe', 'cmd', 'bat']

    def test_get_all_shares(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = shares.Shares(self._filer).get()
        self._filer.get.assert_called_once_with('/config/fileservices/share')
        self.assertEqual(ret, get_response)

    def test_get_share(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = shares.Shares(self._filer).get(self._share_name)
        self._filer.get.assert_called_once_with('/config/fileservices/share/' + self._share_name)
        self.assertEqual(ret, get_response)

    def test_add_cifs_share_default_config_without_acls(self):
        execute_response = self._get_list_physical_folders_response_object()
        self._init_filer(execute_response=execute_response)

        shares.Shares(self._filer).add(self._share_name, self._share_fullpath, [])

        self._filer.execute.assert_called_once_with('/status/fileManager', 'listPhysicalFolders', mock.ANY)
        expected_param = self._get_list_physical_folders_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self._filer.add.assert_called_once_with('/config/fileservices/share', mock.ANY)
        expected_param = self._get_share_object(acl=[])
        actual_param = self._filer.add.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

    def test_add_cifs_share_default_config_with_acls(self):
        execute_response = self._get_list_physical_folders_response_object()
        self._init_filer(execute_response=execute_response)

        shares.Shares(self._filer).add(self._share_name, self._share_fullpath, self._share_acl)

        self._filer.execute.assert_called_once_with('/status/fileManager', 'listPhysicalFolders', mock.ANY)
        expected_param = self._get_list_physical_folders_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self._filer.add.assert_called_once_with('/config/fileservices/share', mock.ANY)  # no verification call param _add_share_acl_rule()

    def test_add_cifs_share_invalid_principal_type(self):
        with self.assertRaises(exception.InputError) as error:
            ShareAccessControlEntry(principal_type='Expected Failure', name='Everyone', perm=FileAccessMode.RO)
        self.assertEqual('Invalid principal type', error.exception.message)

    def test_add_cifs_share_invalid_permission(self):
        with self.assertRaises(exception.InputError) as error:
            ShareAccessControlEntry(principal_type=PrincipalType.LG, name='Everyone', perm='Expected Failure')
        self.assertEqual('Invalid permissions', error.exception.message)

    def test_add_share_failure(self):
        execute_response = self._get_list_physical_folders_response_object()
        self._init_filer(execute_response=execute_response)
        self._filer.add = mock.MagicMock(side_effect=exception.CTERAException())
        with self.assertRaises(exception.CTERAException) as error:
            shares.Shares(self._filer).add(self._share_name, self._share_fullpath, [])

        self._filer.execute.assert_called_once_with('/status/fileManager', 'listPhysicalFolders', mock.ANY)
        expected_param = self._get_list_physical_folders_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self._filer.add.assert_called_once_with('/config/fileservices/share', mock.ANY)
        expected_param = self._get_share_object(acl=[])
        actual_param = self._filer.add.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual('Share creation failed', error.exception.message)

    def test_list_physical_folders_input_error(self):
        execute_response = []
        self._init_filer(execute_response=execute_response)
        with self.assertRaises(exception.InputError) as error:
            shares.Shares(self._filer).add(self._share_name, self._share_fullpath, [])

        self._filer.execute.assert_called_once_with('/status/fileManager', 'listPhysicalFolders', mock.ANY)
        expected_param = self._get_list_physical_folders_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(expected_param, actual_param)

        self.assertEqual('Invalid root directory.', error.exception.message)

    def test_set_share_winacls(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        shares.Shares(self._filer).set_share_winacls(self._share_name)
        self._filer.put.assert_called_once_with('/config/fileservices/share/' + self._share_name + '/access', Acl.WindowsNT)

    def test_block_files_success(self):
        get_response = self._get_share_object()
        self._init_filer(get_response=get_response)
        shares.Shares(self._filer).block_files(self._share_name, self._share_block_files)
        self._filer.get.assert_called_once_with('/config/fileservices/share/' + self._share_name)
        self._filer.put.assert_called_once_with(
            '/config/fileservices/share/' + self._share_name + '/screenedFileTypes',
            self._share_block_files
        )

    def test_block_files_invalid_share_access_type(self):
        get_response = self._get_share_object(access='Expected Failure')
        self._init_filer(get_response=get_response)
        with self.assertRaises(exception.CTERAException) as error:
            shares.Shares(self._filer).block_files(self._share_name, self._share_block_files)
        self._filer.get.assert_called_once_with('/config/fileservices/share/' + self._share_name)
        self.assertEqual('Cannot block file types on non Windows-ACL enabled shares', error.exception.message)

    def test_delete_share_success(self):
        self._init_filer()
        shares.Shares(self._filer).delete(self._share_name)
        self._filer.delete.assert_called_once_with('/config/fileservices/share/' + self._share_name)

    def test_delete_share_failure(self):
        self._filer.delete = mock.MagicMock(side_effect=exception.CTERAException())
        with self.assertRaises(exception.CTERAException) as error:
            shares.Shares(self._filer).delete(self._share_name)
        self.assertEqual('Share deletion failed', error.exception.message)

    def test_modify(self):
        updated_comment = 'Test Modify'
        get_response = self._get_share_object()
        self._init_filer(get_response=get_response)
        modify_command_dict = dict(
            export_to_afp=True,
            export_to_ftp=True,
            export_to_nfs=True,
            export_to_pc_agent=True,
            export_to_rsync=True,
            indexed=True,
            comment=updated_comment,
            access=Acl.OnlyAuthenticatedUsers,
            dir_permissions=644,
        )
        expected_param = self._get_share_object(**modify_command_dict)
        shares.Shares(self._filer).modify(self._share_name, **modify_command_dict)
        self._filer.get.assert_called_once_with('/config/fileservices/share/' + self._share_name)
        self._filer.put.assert_called_once_with('/config/fileservices/share/' + self._share_name, mock.ANY)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(expected_param, actual_param)

    def _get_share_object(self, directory=None, volume=None, acl=None,  # pylint: disable=too-many-arguments
                          access=None, csc=None, dir_permissions=None,
                          comment=None, export_to_afp=False, export_to_ftp=False,
                          export_to_nfs=False, export_to_pc_agent=False,
                          export_to_rsync=False, indexed=False):
        share_param = Object()
        share_param.name = self._share_name
        share_param.directory = self._share_directory if directory is None else directory
        share_param.volume = self._share_volume if volume is None else volume
        share_param.acl = None if acl is None else acl
        share_param.access = Acl.WindowsNT if access is None else access
        share_param.csc = ClientSideCaching.Manual if csc is None else csc
        share_param.dirPermissions = 777 if dir_permissions is None else dir_permissions
        share_param.comment = None if comment is None else comment
        share_param.exportToAFP = False if export_to_afp is None else export_to_afp
        share_param.exportToFTP = False if export_to_ftp is None else export_to_ftp
        share_param.exportToNFS = False if export_to_nfs is None else export_to_nfs
        share_param.exportToPCAgent = False if export_to_pc_agent is None else export_to_pc_agent
        share_param.exportToRSync = False if export_to_rsync is None else export_to_rsync
        share_param.indexed = False if indexed is None else indexed
        return share_param

    def _get_list_physical_folders_param(self):
        list_physical_folders_param = Object()
        list_physical_folders_param.path = self._root
        return list_physical_folders_param

    def _get_list_physical_folders_response_object(self, name=None, fullpath=None):
        list_physical_folders_response = Object()
        list_physical_folders_response.name = self._share_volume if name is None else name
        list_physical_folders_response.type = 'some type'
        list_physical_folders_response.fullpath = (self._root + self._share_volume) if fullpath is None else fullpath
        return [list_physical_folders_response]
