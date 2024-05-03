import logging

from . import enum
from .files import common
from ..common import Object
from ..exceptions import CTERAException, InputError
from .base_command import BaseCommand
from .types import NFSv3AccessControlEntry, RemoveNFSv3AccessControlEntry, ShareAccessControlEntry, RemoveShareAccessControlEntry


class Shares(BaseCommand):

    def get(self, name=None):
        """
        Get Share. If a share name was not passed as an argument, a list of all shares will be retrieved
        :param str,optional name: Name of the share
        """
        return self._edge.api.get('/config/fileservices/share' + ('' if name is None else ('/' + name)))

    def add(self,
            name,
            directory,
            acl=None,
            access=enum.Acl.WindowsNT,
            csc=enum.ClientSideCaching.Manual,
            dir_permissions=777,
            comment=None,
            export_to_afp=False,
            export_to_ftp=False,
            export_to_nfs=False,
            export_to_pc_agent=False,
            export_to_rsync=False,
            indexed=False,
            trusted_nfs_clients=None,
            uuid=None
            ):  # pylint: disable=too-many-arguments,too-many-locals,unused-argument
        """
        Add a network share.

        :param str name: The share name
        :param str directory: Full directory path
        :param list[cterasdk.edge.types.ShareAccessControlEntry] acl: List of access control entries
        :param cterasdk.edge.enum.Acl access: The Windows File Sharing authentication mode, defaults to ``winAclMode``
        :param cterasdk.edge.enum.ClientSideCaching csc: The client side caching (offline files) configuration, defaults to ``manual``
        :param int dir_permissions: Directory Permission, defaults to 777
        :param str comment: Comment
        :param bool export_to_afp: Whether to enable AFP access, defaults to ``False``
        :param bool export_to_ftp: Whether to enable FTP access, defaults to ``False``
        :param bool export_to_nfs: Whether to enable NFS access, defaults to ``False``
        :param bool export_to_pc_agent: Whether to allow as a destination share for CTERA Backup Agents, defaults to ``False``
        :param bool export_to_rsync: Whether to enable access over rsync, defaults to ``False``
        :param bool indexed: Whether to enable indexing for search, defaults to ``False``
        :param list[cterasdk.edge.types.NFSv3AccessControlEntry] trusted_nfs_clients: Trusted NFS v3 clients, defaults to ``None``
        """
        acl = acl or []

        param = Object()
        param.name = name

        parts = common.Path(directory, '/').parts()
        volume = parts[0]
        self._validate_root_directory(volume)
        param.volume = volume

        directory = '/'.join(parts[1:])
        param.directory = directory

        param.access = access
        param.clientSideCaching = csc
        param.dirPermissions = dir_permissions
        param.exportToAFP = export_to_afp
        param.exportToFTP = export_to_ftp
        param.exportToNFS = export_to_nfs
        param.exportToPCAgent = export_to_pc_agent
        param.exportToRSync = export_to_rsync
        param.indexed = indexed
        param.comment = comment
        Shares._validate_acl(acl)
        param.acl = [acl_entry.to_server_object() for acl_entry in acl]
        param.trustedNFSClients = [client.to_server_object() for client in (trusted_nfs_clients or [])]
        if uuid:
            param._uuid = uuid  # pylint: disable=protected-access

        try:
            self._edge.api.add('/config/fileservices/share', param)
            logging.getLogger('cterasdk.edge').info("Share created. %s", {'name': name})
        except Exception as error:
            logging.getLogger('cterasdk.edge').error("Share creation failed.")
            raise CTERAException('Share creation failed', error)

    def set_share_winacls(self, name):
        """
        Set a network share to use Windows ACL Emulation Mode

        :param str name: The share name
        """
        logging.getLogger('cterasdk.edge').error("Updating Windows file sharing access mode. %s",
                                                 {'share': name, 'access': enum.Acl.WindowsNT})
        self._edge.api.put('/config/fileservices/share/' + name + '/access', enum.Acl.WindowsNT)

    def get_access_type(self, name):
        """
        Get the network share Windows File Sharing authentication mode

        :param str name: The share name
        """
        return self._edge.api.get('/config/fileservices/share/' + name + '/access')

    def set_access_type(self, name, access):
        """
        Set the network share Windows File Sharing authentication mode

        :param str name: The share name
        :param cterasdk.edge.enum.Acl access: The Windows File Sharing authentication mode
        """
        logging.getLogger('cterasdk.edge').info("Updating Windows file sharing access mode. %s", {'share': name, 'access': access})
        self._edge.api.put('/config/fileservices/share/' + name + '/access', access)

    def block_files(self, name, extensions):
        """
        Configure a share to block one or more file extensions

        :param str name: The share name
        :param list[str] extensions: List of file extensions to block
        """
        share = self.get(name)
        if share.access != enum.Acl.WindowsNT:
            raise CTERAException('Cannot block file types on non Windows-ACL enabled shares', None, share=share.name, access=share.access)
        logging.getLogger('cterasdk.edge').error("Updating the list of blocked file extensions. %s",
                                                 {'share': name, 'extensions': extensions, 'access': enum.Acl.WindowsNT})
        self._edge.api.put('/config/fileservices/share/' + share.name + '/screenedFileTypes', extensions)

    def set_acl(self, name, acl):
        """
        Set a network share's access control entries.

        :param str name: The share name
        :param list[cterasdk.edge.types.ShareAccessControlEntry] acl: List of access control entries

        .. warning:: this method will override the existing access control entries
        """
        Shares._validate_acl(acl)

        param = [acl_entry.to_server_object() for acl_entry in acl]
        self._edge.api.put('/config/fileservices/share/' + name + '/acl', param)

    def add_acl(self, name, acl):
        """
        Add one or more access control entries to an existing share.

        :param str name: The share name
        :param list[cterasdk.edge.types.ShareAccessControlEntry] acl: List of access control entries to add
        """
        Shares._validate_acl(acl)

        current_acl = self.get_acl(name)

        new_acl_dict = {
            acl_entry.principal_type + '#' + acl_entry.name: acl_entry.to_server_object()
            for acl_entry in acl
        }

        for entry in current_acl:
            ace = ShareAccessControlEntry.from_server_object(entry)
            entry_key = ace.principal_type + '#' + ace.name
            if entry_key not in new_acl_dict:
                new_acl_dict[entry_key] = entry

        acls_array = [v for k, v in new_acl_dict.items()]
        self._edge.api.put('/config/fileservices/share/' + name + '/acl', acls_array)

    def remove_acl(self, name, acl):
        """
        Remove one or more access control entries from an existing share.

        :param str name: The share name
        :param list[cterasdk.edge.types.RemoveShareAccessControlEntry] acl: List of access control entries to remove
        """
        Shares._validate_remove_acl(acl)

        remove_acl_dict = {
            acl_entry.principal_type + '#' + acl_entry.name: True
            for acl_entry in acl
        }

        current_acl = self.get_acl(name)

        new_acl = []
        for entry in current_acl:
            ace = ShareAccessControlEntry.from_server_object(entry)
            if not remove_acl_dict.get(ace.principal_type + '#' + ace.name, False):
                new_acl.append(entry)

        self._edge.api.put('/config/fileservices/share/' + name + '/acl', new_acl)

    def get_acl(self, name):
        """
        Get the current access control entries from an existing share.

        :param str name: The share name
        """
        return self._edge.api.get('/config/fileservices/share/' + name + '/acl')

    def modify(
            self,
            name,
            directory=None,
            acl=None,
            access=None,
            csc=None,
            dir_permissions=None,
            comment=None,
            export_to_afp=None,
            export_to_ftp=None,
            export_to_nfs=None,
            export_to_pc_agent=None,
            export_to_rsync=None,
            indexed=None,
            trusted_nfs_clients=None
                ):  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,unused-argument
        """
        Modify an existing network share. All parameters but name are optional and default to None

        :param str name: The share name
        :param str,optional directory: Full directory path
        :param list[cterasdk.edge.types.ShareAccessControlEntry],optional acl: List of access control entries
        :param cterasdk.edge.enum.Acl,optional access: The Windows File Sharing authentication mode
        :param cterasdk.edge.enum.ClientSideCaching,optional csc: The client side caching (offline files) configuration
        :param int,optional dir_permissions: Directory Permission
        :param str,optional comment: Comment
        :param bool,optional export_to_afp: Whether to enable AFP access
        :param bool,optional export_to_ftp: Whether to enable FTP access
        :param bool,optional export_to_nfs: Whether to enable NFS access
        :param bool,optional export_to_pc_agent: Whether to allow as a destination share for CTERA Backup Agents
        :param bool,optional export_to_rsync: Whether to enable access over rsync
        :param bool,optional indexed: Whether to enable indexing for search
        :param list[cterasdk.edge.types.NFSv3AccessControlEntry] trusted_nfs_clients: Trusted NFS v3 clients, defaults to ``None``
        """
        share = self.get(name=name)
        if directory is not None:
            parts = common.Path(directory, '/').parts()
            volume = parts[0]
            self._validate_root_directory(volume)
            share.volume = volume
            directory = '/'.join(parts[1:])
            share.directory = directory
        if access is not None:
            share.access = access
        if csc is not None:
            share.clientSideCaching = csc
        if dir_permissions is not None:
            share.dirPermissions = dir_permissions
        if export_to_afp is not None:
            share.exportToAFP = export_to_afp
        if export_to_ftp is not None:
            share.exportToFTP = export_to_ftp
        if export_to_nfs is not None:
            share.exportToNFS = export_to_nfs
        if export_to_pc_agent is not None:
            share.exportToPCAgent = export_to_pc_agent
        if export_to_rsync is not None:
            share.exportToRSync = export_to_rsync
        if indexed is not None:
            share.indexed = indexed
        if comment is not None:
            share.comment = comment
        if acl is not None:
            Shares._validate_acl(acl)
            share.acl = [acl_entry.to_server_object() for acl_entry in acl]
        if trusted_nfs_clients is not None:
            share.trustedNFSClients = [client.to_server_object() for client in trusted_nfs_clients]

        try:
            self._edge.api.put('/config/fileservices/share/' + name, share)
            logging.getLogger('cterasdk.edge').info("Share modified. %s", {'name': name})
        except Exception as error:
            msg = f'Failed to modify the share {name}'
            logging.getLogger('cterasdk.edge').error(msg)
            raise CTERAException(msg, error)

    def delete(self, name):
        """
        Delete a share.

        :param str name: The share name
        """
        try:
            self._edge.api.delete('/config/fileservices/share/' + name)
            logging.getLogger('cterasdk.edge').info("Share deleted. %s", {'name': name})
        except Exception as error:
            logging.getLogger('cterasdk.edge').error("Share deletion failed.")
            raise CTERAException('Share deletion failed', error)

    def get_trusted_nfs_clients(self, name):
        """
        Get the current trusted NFS client entries from an existing share.

        :param str name: The share name
        """
        return self._edge.api.get('/config/fileservices/share/' + name + '/trustedNFSClients')

    def set_trusted_nfs_clients(self, name, trusted_nfs_clients):
        """
        Set a network share's trusted NFS client entries.

        :param str name: The share name
        :param list[cterasdk.edge.types.NFSv3AccessControlEntry] trusted_nfs_clients: Trusted NFS v3 clients

        .. warning:: this method will override the existing access control entries
        """
        Shares._validate_trusted_nfs_clients(trusted_nfs_clients)

        param = [client.to_server_object() for client in (trusted_nfs_clients or [])]
        self._edge.api.put('/config/fileservices/share/' + name + '/trustedNFSClients', param)

    def add_trusted_nfs_clients(self, name, trusted_nfs_clients):
        """
        Add one or more trusted NFS client entries to an existing share.

        :param str name: The share name
        :param list[cterasdk.edge.types.NFSv3AccessControlEntry] trusted_nfs_clients: Trusted NFS v3 clients
        """
        Shares._validate_trusted_nfs_clients(trusted_nfs_clients)

        new_trusted_nfs_clients_dict = {
            trusted_nfs_client.address + '#' + trusted_nfs_client.netmask: trusted_nfs_client.to_server_object()
            for trusted_nfs_client in trusted_nfs_clients
        }

        def entry_not_in_new(entry):
            trusted_nfs_client = NFSv3AccessControlEntry.from_server_object(entry)
            entry_key = trusted_nfs_client.address + '#' + trusted_nfs_client.netmask
            return entry_key not in new_trusted_nfs_clients_dict

        param = list(new_trusted_nfs_clients_dict.values()) + list(filter(entry_not_in_new, self.get_trusted_nfs_clients(name)))

        self._edge.api.put('/config/fileservices/share/' + name + '/trustedNFSClients', param)

    def remove_trusted_nfs_clients(self, name, trusted_nfs_clients):
        """
        Remove one or more trusted NFS client entries from an existing share.

        :param str name: The share name
        :param list[cterasdk.edge.types.RemoveNFSv3AccessControlEntry] trusted_nfs_clients: Trusted NFS v3 clients
        """
        Shares._validate_remove_trusted_nfs_clients(trusted_nfs_clients)

        remove_trusted_nfs_clients_dict = {
            trusted_nfs_client.address + '#' + trusted_nfs_client.netmask
            for trusted_nfs_client in trusted_nfs_clients
        }

        def entry_not_removed(entry):
            trusted_nfs_client = NFSv3AccessControlEntry.from_server_object(entry)
            entry_key = trusted_nfs_client.address + '#' + trusted_nfs_client.netmask
            return entry_key not in remove_trusted_nfs_clients_dict

        param = list(filter(entry_not_removed, self.get_trusted_nfs_clients(name)))
        self._edge.api.put('/config/fileservices/share/' + name + '/trustedNFSClients', param)

    def get_screened_file_types(self, name):
        """
        Get the share's current list of blocked file extensions

        :param str name: The share name
        """
        return self._edge.api.get('/config/fileservices/share/' + name + '/screenedFileTypes')

    def set_screened_file_types(self, name, extensions):
        """
        Set the share's current list of blocked file extensions (override the current list)

        :param str name: The share name
        :param list[str] extensions: List of file extensions to block
        """
        share = self.get(name)
        if share.access != enum.Acl.WindowsNT:
            raise CTERAException('Cannot block file types on non Windows-ACL enabled shares', None, share=share.name, access=share.access)
        logging.getLogger('cterasdk.edge').info(
            "Updating the list of blocked file extensions. %s",
            {'share': name, 'extensions': extensions, 'access': enum.Acl.WindowsNT}
        )
        self._edge.api.put('/config/fileservices/share/' + share.name + '/screenedFileTypes', extensions)

    def add_screened_file_types(self, name, extensions):
        """
        Add extensions to the share's current list of blocked file extensions

        :param str name: The share name
        :param list[str] extensions: List of file extensions to add
        """
        share = self.get(name)
        if share.access != enum.Acl.WindowsNT:
            raise CTERAException('Cannot block file types on non Windows-ACL enabled shares', None, share=share.name, access=share.access)

        new_list = list(set(share.screenedFileTypes + extensions))

        logging.getLogger('cterasdk.edge').info(
            "Updating the list of blocked file extensions. %s",
            {'share': name, 'extensions': new_list, 'access': enum.Acl.WindowsNT}
        )
        self._edge.api.put('/config/fileservices/share/' + share.name + '/screenedFileTypes', new_list)

    def remove_screened_file_types(self, name, extensions):
        """
        Remove extensions from the share's current list of blocked file extensions

        :param str name: The share name
        :param list[str] extensions: List of file extensions to remove
        """
        share = self.get(name)
        if share.access != enum.Acl.WindowsNT:
            raise CTERAException('Cannot block file types on non Windows-ACL enabled shares', None, share=share.name, access=share.access)

        new_list = list(set(share.screenedFileTypes) - set(extensions))

        logging.getLogger('cterasdk.edge').info(
            "Updating the list of blocked file extensions. %s",
            {'share': name, 'extensions': new_list, 'access': enum.Acl.WindowsNT}
        )
        self._edge.api.put('/config/fileservices/share/' + share.name + '/screenedFileTypes', new_list)

    def _validate_root_directory(self, name):
        param = Object()
        param.path = '/'

        response = self._edge.api.execute('/status/fileManager', 'listPhysicalFolders', param)
        for root in response:
            if root.fullpath == f'/{name}':
                logging.getLogger('cterasdk.edge').debug("Found root directory. %s",
                                                         {'name': root.name, 'type': root.type, 'fullpath': root.fullpath})
                return name

        logging.getLogger('cterasdk.edge').error("Could not find root directory. %s", {'name': name})

        options = [root.fullpath[1:] for root in response]
        raise InputError('Invalid root directory.', name, options)

    @staticmethod
    def _validate_acl(acl):
        if not isinstance(acl, list):
            raise InputError('Invalid access control list format', repr(acl), '[cterasdk.edge.types.ShareAccessControlEntry, ...]')
        for acl_entry in acl:
            if not isinstance(acl_entry, ShareAccessControlEntry):
                raise InputError('Invalid access control entry format', repr(acl_entry), 'cterasdk.edge.types.ShareAccessControlEntry')

    @staticmethod
    def _validate_remove_acl(acl):
        if not isinstance(acl, list):
            raise InputError('Invalid access control list format', repr(acl), '[cterasdk.edge.types.RemoveShareAccessControlEntry, ...]')
        for acl_entry in acl:
            if not isinstance(acl_entry, RemoveShareAccessControlEntry):
                raise InputError(
                    'Invalid access control entry format',
                    repr(acl_entry),
                    'cterasdk.edge.types.RemoveShareAccessControlEntry'
                )

    @staticmethod
    def _validate_trusted_nfs_clients(trusted_nfs_clients):
        if not isinstance(trusted_nfs_clients, list):
            raise InputError(
                'Invalid Trusted NFS Clients list format',
                repr(trusted_nfs_clients),
                '[cterasdk.edge.types.NFSv3AccessControlEntry, ...]'
            )
        for entry in trusted_nfs_clients:
            if not isinstance(entry, NFSv3AccessControlEntry):
                raise InputError('Invalid Trusted NFS Clients entry format', repr(entry), 'cterasdk.edge.types.NFSv3AccessControlEntry')

    @staticmethod
    def _validate_remove_trusted_nfs_clients(trusted_nfs_clients):
        if not isinstance(trusted_nfs_clients, list):
            raise InputError(
                'Invalid Trusted NFS Clients list format',
                repr(trusted_nfs_clients),
                '[cterasdk.edge.types.RemoveNFSv3AccessControlEntry, ...]'
            )
        for entry in trusted_nfs_clients:
            if not isinstance(entry, RemoveNFSv3AccessControlEntry):
                raise InputError(
                    'Invalid Trusted NFS Clients entry format',
                    repr(entry),
                    'cterasdk.edge.types.RemoveNFSv3AccessControlEntry'
                )
