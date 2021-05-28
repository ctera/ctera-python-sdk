from unittest import mock

from cterasdk import exception
from cterasdk.edge import shares
from cterasdk.edge.enum import Acl, ClientSideCaching, PrincipalType, FileAccessMode
from cterasdk.edge.types import ShareAccessControlEntry, NFSv3AccessControlEntry, RemoveNFSv3AccessControlEntry
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeShares(base_edge.BaseEdgeTest):  # pylint: disable=too-many-public-methods

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
        self._trusted_nfs_clients = [
            NFSv3AccessControlEntry(address='192.168.0.1', netmask='255.255.240.0', perm=FileAccessMode.RW),
            NFSv3AccessControlEntry(address='10.0.0.1', netmask='255.255.0.0', perm=FileAccessMode.RO),
            NFSv3AccessControlEntry(address='172.0.17.3', netmask='0.0.0.0', perm=FileAccessMode.NA)
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
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.add.assert_called_once_with('/config/fileservices/share', mock.ANY)
        expected_param = self._get_share_object(acl=[])
        actual_param = self._filer.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_add_cifs_share_default_config_with_acls(self):
        execute_response = self._get_list_physical_folders_response_object()
        self._init_filer(execute_response=execute_response)

        shares.Shares(self._filer).add(self._share_name, self._share_fullpath, self._share_acl)

        self._filer.execute.assert_called_once_with('/status/fileManager', 'listPhysicalFolders', mock.ANY)
        expected_param = self._get_list_physical_folders_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.add.assert_called_once_with('/config/fileservices/share', mock.ANY)  # no verification call param _add_share_acl_rule()

    def test_add_nfs_v3_share_success(self):
        execute_response = self._get_list_physical_folders_response_object()
        self._init_filer(execute_response=execute_response)

        shares.Shares(self._filer).add(self._share_name, self._share_fullpath, export_to_nfs=True,
                                       trusted_nfs_clients=self._trusted_nfs_clients)

        self._filer.execute.assert_called_once_with('/status/fileManager', 'listPhysicalFolders', mock.ANY)
        expected_param = self._get_list_physical_folders_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self._filer.add.assert_called_once_with('/config/fileservices/share', mock.ANY)

        expected_param = self._get_share_object(acl=[], export_to_nfs=True,
                                                trusted_nfs_clients=[client.to_server_object() for client in self._trusted_nfs_clients])
        actual_param = self._filer.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_modify_nfs_v3_share_success(self):
        get_response = self._get_share_object(export_to_nfs=False)
        self._init_filer(get_response=get_response)

        shares.Shares(self._filer).modify(self._share_name, export_to_nfs=True, trusted_nfs_clients=self._trusted_nfs_clients)

        self._filer.get.assert_called_once_with('/config/fileservices/share/' + self._share_name)
        self._filer.put.assert_called_once_with('/config/fileservices/share/' + self._share_name, mock.ANY)

        expected_param = self._get_share_object(export_to_nfs=True,
                                                trusted_nfs_clients=[client.to_server_object() for client in self._trusted_nfs_clients])
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

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
        self._assert_equal_objects(actual_param, expected_param)

        self._filer.add.assert_called_once_with('/config/fileservices/share', mock.ANY)
        expected_param = self._get_share_object(acl=[])
        actual_param = self._filer.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual('Share creation failed', error.exception.message)

    def test_list_physical_folders_input_error(self):
        execute_response = []
        self._init_filer(execute_response=execute_response)
        with self.assertRaises(exception.InputError) as error:
            shares.Shares(self._filer).add(self._share_name, self._share_fullpath, [])

        self._filer.execute.assert_called_once_with('/status/fileManager', 'listPhysicalFolders', mock.ANY)
        expected_param = self._get_list_physical_folders_param()
        actual_param = self._filer.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

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
            csc=ClientSideCaching.Disabled
        )
        expected_param = self._get_share_object(**modify_command_dict)
        shares.Shares(self._filer).modify(self._share_name, **modify_command_dict)
        self._filer.get.assert_called_once_with('/config/fileservices/share/' + self._share_name)
        self._filer.put.assert_called_once_with('/config/fileservices/share/' + self._share_name, mock.ANY)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def _get_share_object(self, directory=None, volume=None, acl=None,  # pylint: disable=too-many-arguments,too-many-locals
                          access=None, csc=None, dir_permissions=None,
                          comment=None, export_to_afp=False, export_to_ftp=False,
                          export_to_nfs=False, export_to_pc_agent=False,
                          export_to_rsync=False, indexed=False, trusted_nfs_clients=None):
        share_param = Object()
        share_param.name = self._share_name
        share_param.directory = self._share_directory if directory is None else directory
        share_param.volume = self._share_volume if volume is None else volume
        share_param.acl = None if acl is None else acl
        share_param.access = Acl.WindowsNT if access is None else access
        share_param.clientSideCaching = ClientSideCaching.Manual if csc is None else csc
        share_param.dirPermissions = 777 if dir_permissions is None else dir_permissions
        share_param.comment = None if comment is None else comment
        share_param.exportToAFP = False if export_to_afp is None else export_to_afp
        share_param.exportToFTP = False if export_to_ftp is None else export_to_ftp
        share_param.exportToNFS = False if export_to_nfs is None else export_to_nfs
        share_param.exportToPCAgent = False if export_to_pc_agent is None else export_to_pc_agent
        share_param.exportToRSync = False if export_to_rsync is None else export_to_rsync
        share_param.indexed = False if indexed is None else indexed
        share_param.trustedNFSClients = [] if trusted_nfs_clients is None else trusted_nfs_clients
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

    def test_get_acl(self):
        share_name = 'share'
        get_response = self._get_acl_object()
        self._init_filer(get_response=[get_response.to_server_object()])
        acl = shares.Shares(self._filer).get_acl(share_name)
        self._filer.get.assert_called_once_with('/config/fileservices/share/' + share_name + '/acl')
        self._assert_equal_objects(ShareAccessControlEntry.from_server_object(acl[0]), get_response)

    @staticmethod
    def _get_acl_object():
        return ShareAccessControlEntry(principal_type=PrincipalType.LG, name='Everyone', perm=FileAccessMode.RO)

    def test_get_trusted_nfs_clients(self):
        share_name = 'share'
        get_response = self._get_get_trusted_nfs_client_object()
        self._init_filer(get_response=[get_response.to_server_object()])
        trusted_nfs_clients = shares.Shares(self._filer).get_trusted_nfs_clients(share_name)
        self._filer.get.assert_called_once_with('/config/fileservices/share/' + share_name + '/trustedNFSClients')
        self._assert_equal_objects(NFSv3AccessControlEntry.from_server_object(trusted_nfs_clients[0]), get_response)

    def test_set_trusted_nfs_clients(self):
        share_name = 'share'
        new_trusted_nfs_clients = self._get_get_trusted_nfs_client_object()
        self._init_filer()
        shares.Shares(self._filer).set_trusted_nfs_clients(share_name, [new_trusted_nfs_clients])
        self._filer.put.assert_called_once_with('/config/fileservices/share/' + share_name + '/trustedNFSClients', mock.ANY)
        expected_param = new_trusted_nfs_clients.to_server_object()
        actual_param = self._filer.put.call_args[0][1][0]
        self._assert_equal_objects(actual_param, expected_param)

    def test_add_trusted_nfs_clients(self):
        share_name = 'share'
        current_trusted_nfs_clients = self._get_get_trusted_nfs_client_object()
        self._init_filer(get_response=[current_trusted_nfs_clients.to_server_object()])

        new_trusted_nfs_clients = self._get_get_trusted_nfs_client_object(address="192.168.0.0")
        shares.Shares(self._filer).add_trusted_nfs_clients(share_name, [new_trusted_nfs_clients])
        self._filer.put.assert_called_once_with('/config/fileservices/share/' + share_name + '/trustedNFSClients', mock.ANY)

        def get_address(elem):
            return elem.address

        actual_param = self._filer.put.call_args[0][1]
        actual_param.sort(key=get_address)

        expected_param = [current_trusted_nfs_clients.to_server_object(), new_trusted_nfs_clients.to_server_object()]
        expected_param.sort(key=get_address)

        self.assertEqual(len(expected_param), len(actual_param))

        for i in range(len(actual_param)):  # pylint: disable=consider-using-enumerate
            self._assert_equal_objects(actual_param[i], expected_param[i])

    def test_remove_trusted_nfs_clients(self):
        share_name = 'share'
        trusted_nfs_client_to_keep = self._get_get_trusted_nfs_client_object(address="192.168.0.0")
        trusted_nfs_client_to_remove = self._get_get_trusted_nfs_client_object(address="192.168.1.0")
        self._init_filer(get_response=[trusted_nfs_client_to_keep.to_server_object(), trusted_nfs_client_to_remove.to_server_object()])

        shares.Shares(self._filer).remove_trusted_nfs_clients(
            share_name,
            [
                RemoveNFSv3AccessControlEntry(trusted_nfs_client_to_remove.address, trusted_nfs_client_to_remove.netmask)
            ]
        )
        self._filer.put.assert_called_once_with('/config/fileservices/share/' + share_name + '/trustedNFSClients', mock.ANY)

        expected_param = trusted_nfs_client_to_keep.to_server_object()
        actual_param = self._filer.put.call_args[0][1][0]
        self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_get_trusted_nfs_client_object(address=None):
        return NFSv3AccessControlEntry(address=address or '192.168.68.0', netmask='255.255.255.0', perm=FileAccessMode.RO)
