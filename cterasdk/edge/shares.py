import logging

from . import enum
from .files import path
from ..common import Object
from ..exception import CTERAException, InputError
from .base_command import BaseCommand
from .types import ShareAccessControlEntry, RemoveShareAccessControlEntry


class Shares(BaseCommand):

    def get(self, name=None):
        """
        Get Share. If a share name was not passed as an argument, a list of all shares will be retrieved
        :param str,optional name: Name of the share
        """
        return self._gateway.get('/config/fileservices/share' + ('' if name is None else ('/' + name)))

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
            indexed=False
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
        """
        acl = acl or []

        param = Object()
        param.name = name

        parts = path.CTERAPath(directory, '/').parts()
        volume = parts[0]
        self._validate_root_directory(volume)
        param.volume = volume

        directory = '/'.join(parts[1:])
        param.directory = directory

        param.access = access
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

        try:
            self._gateway.add('/config/fileservices/share', param)
            logging.getLogger().info("Share created. %s", {'name': name})
        except Exception as error:
            logging.getLogger().error("Share creation failed.")
            raise CTERAException('Share creation failed', error)

    def set_share_winacls(self, name):
        """
        Set a network share to use Windows ACL Emulation Mode

        :param str name: The share name
        """
        logging.getLogger().error("Updating Windows file sharing access mode. %s", {'share': name, 'access': enum.Acl.WindowsNT})
        self._gateway.put('/config/fileservices/share/' + name + '/access', enum.Acl.WindowsNT)

    def block_files(self, name, extensions):
        """
        Configure a share to block one or more file extensions

        :param str name: The share name
        :param list[str] extensions: List of file extensions to block
        """
        share = self.get(name)
        if share.access != enum.Acl.WindowsNT:
            raise CTERAException('Cannot block file types on non Windows-ACL enabled shares', None, share=share.name, access=share.access)
        logging.getLogger().error("Updating the list of blocked file extensions. %s",
                                  {'share': name, 'extensions': extensions, 'access': enum.Acl.WindowsNT})
        self._gateway.put('/config/fileservices/share/' + share.name + '/screenedFileTypes', extensions)

    def set_acl(self, name, acl):
        """
        Set a network share's access control entries.

        :param str name: The share name
        :param list[cterasdk.edge.types.ShareAccessControlEntry] acl: List of access control entries

        .. warning:: this method will override the existing access control entries
        """
        Shares._validate_acl(acl)

        param = [acl_entry.to_server_object() for acl_entry in acl]
        self._gateway.put('/config/fileservices/share/' + name + '/acl', param)

    def add_acl(self, name, acl):
        """
        Add one or more access control entries to an existing share.

        :param str name: The share name
        :param list[cterasdk.edge.types.ShareAccessControlEntry] acl: List of access control entries to add
        """
        Shares._validate_acl(acl)

        current_acl = self._gateway.get('/config/fileservices/share/' + name + '/acl')

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
        self._gateway.put('/config/fileservices/share/' + name + '/acl', acls_array)

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

        current_acl = self._gateway.get('/config/fileservices/share/' + name + '/acl')

        new_acl = []
        for entry in current_acl:
            ace = ShareAccessControlEntry.from_server_object(entry)
            if not remove_acl_dict.get(ace.principal_type + '#' + ace.name, False):
                new_acl.append(entry)

        self._gateway.put('/config/fileservices/share/' + name + '/acl', new_acl)

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
            indexed=None
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
        """
        share = self.get(name=name)
        if directory is not None:
            parts = path.CTERAPath(directory, '/').parts()
            volume = parts[0]
            self._validate_root_directory(volume)
            share.volume = volume
            directory = '/'.join(parts[1:])
            share.directory = directory
        if access is not None:
            share.access = access
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

        try:
            self._gateway.put('/config/fileservices/share/' + name, share)
            logging.getLogger().info("Share modified. %s", {'name': name})
        except Exception as error:
            msg = 'Failed to modify the share %s' % name
            logging.getLogger().error(msg)
            raise CTERAException(msg, error)

    def delete(self, name):
        """
        Delete a share.

        :param str name: The share name
        """
        try:
            self._gateway.delete('/config/fileservices/share/' + name)
            logging.getLogger().info("Share deleted. %s", {'name': name})
        except Exception as error:
            logging.getLogger().error("Share deletion failed.")
            raise CTERAException('Share deletion failed', error)

    def _validate_root_directory(self, name):
        param = Object()
        param.path = '/'

        response = self._gateway.execute('/status/fileManager', 'listPhysicalFolders', param)
        for root in response:
            if root.fullpath == ('/%s' % name):
                logging.getLogger().debug("Found root directory. %s", {'name': root.name, 'type': root.type, 'fullpath': root.fullpath})
                return name

        logging.getLogger().error("Could not find root directory. %s", {'name': name})

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
