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
            dirPermissions=777,
            comment=None,
            exportToAFP=False,
            exportToFTP=False,
            exportToNFS=False,
            exportToPCAgent=False,
            exportToRSync=False,
            indexed=False
            ):  # pylint: disable=too-many-arguments,too-many-locals
        """
        Add a network share.

        :param str name: the share name
        :param str directory: full directory path
        :param list[cterasdk.edge.types.ShareAccessControlEntry] acl: a list of 3-tuple access control entries
        :param str access: the Windows File Sharing authentication mode, defaults to ``winAclMode``
        :param str csc: the client side caching (offline files) configuration, defaults to ``manual``
        :param str comment: comment
        :param bool exportToAFP: whether to enable AFP access, defaults to ``False``
        :param bool exportToFTP: whether to enable FTP access, defaults to ``False``
        :param bool exportToNFS: whether to enable NFS access, defaults to ``False``
        :param bool exportToPCAgent: whether to allow as a destination share for CTERA Backup Agents, defaults to ``False``
        :param bool exportToRSync: whether to enable access over rsync, defaults to ``False``
        """
        param = Object()
        param.name = name

        parts = path.CTERAPath(directory, '/').parts()
        volume = parts[0]
        self._validate_root_directory(volume)
        param.volume = volume

        directory = '/'.join(parts[1:])
        param.directory = directory

        param.access = access
        param.dirPermissions = dirPermissions
        param.exportToAFP = exportToAFP
        param.exportToFTP = exportToFTP
        param.exportToNFS = exportToNFS
        param.exportToPCAgent = exportToPCAgent
        param.exportToRSync = exportToRSync
        param.indexed = indexed
        param.comment = comment
        param.acl = []

        Shares._validate_acl(acl)
        for acl_entry in acl:
            Shares._add_share_acl_rule(param.acl, acl_entry)

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

        .. warning: this method will override the existing access control entries
        """
        Shares._validate_acl(acl)

        param = []
        for acl_entry in acl:
            Shares._add_share_acl_rule(param, acl_entry)
        self._gateway.put('/config/fileservices/share/' + name + '/acl', param)

    def add_acl(self, name, acl):
        """
        Add one or more access control entries to an existing share.

        :param str name: The share name
        :param list[cterasdk.edge.types.ShareAccessControlEntry] acl: List of access control entries to add
        """
        Shares._validate_acl(acl)

        current_acl = self._gateway.get('/config/fileservices/share/' + name + '/acl')

        new_acl_dict = {}
        for acl_entry in acl:
            temp_acl = []
            Shares._add_share_acl_rule(temp_acl, acl_entry)
            entry_key = acl_entry.type + '#' + acl_entry.name
            new_acl_dict[entry_key] = temp_acl[0]

        for entry in current_acl:
            ace_type = entry.principal2._classname  # pylint: disable=protected-access
            if ace_type in [enum.PrincipalType.LU, enum.PrincipalType.LG]:
                ace_name = entry.principal2.ref
                ace_name = ace_name[ace_name.rfind('#') + 1:]
            else:
                ace_name = entry.principal2.name
            entry_key = ace_type + '#' + ace_name

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

        current_acl = self._gateway.get('/config/fileservices/share/' + name + '/acl')

        options = {v: k for k, v in enum.PrincipalType.__dict__.items() if not k.startswith('_')}  # reverse
        new_acl = []
        for entry in current_acl:
            ace_type = entry.principal2._classname  # pylint: disable=protected-access
            if ace_type in [enum.PrincipalType.LU, enum.PrincipalType.LG]:
                ace_name = entry.principal2.ref
                ace_name = ace_name[ace_name.rfind('#') + 1:]
            else:
                ace_name = entry.principal2.name

            if RemoveShareAccessControlEntry(type=options.get(ace_type), name=ace_name) not in acl:
                new_acl.append(entry)

        self._gateway.put('/config/fileservices/share/' + name + '/acl', new_acl)

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
    def _add_share_acl_rule(acls, acl_entry):
        ace = Object()
        ace._classname = "ShareACLRule"  # pylint: disable=protected-access
        ace.principal2 = Object()

        options = {k: v for k, v in enum.PrincipalType.__dict__.items() if not k.startswith('_')}
        principal_type = options.get(acl_entry.type)
        if principal_type == enum.PrincipalType.LU:
            ace.principal2._classname = enum.PrincipalType.LU  # pylint: disable=protected-access
            ace.principal2.ref = "#config#auth#users#" + acl_entry.name
        elif principal_type == enum.PrincipalType.LG:
            ace.principal2._classname = enum.PrincipalType.LG  # pylint: disable=protected-access
            ace.principal2.ref = "#config#auth#groups#" + acl_entry.name
        elif principal_type == enum.PrincipalType.DU:
            ace.principal2._classname = enum.PrincipalType.DU  # pylint: disable=protected-access
            ace.principal2.name = acl_entry.name
        elif principal_type == enum.PrincipalType.DG:
            ace.principal2._classname = enum.PrincipalType.DG  # pylint: disable=protected-access
            ace.principal2.name = acl_entry.name
        else:
            raise InputError('Invalid principal type', acl_entry.type, list(options.keys()))

        ace.permissions = Object()
        ace.permissions._classname = "FileAccessPermissions"  # pylint: disable=protected-access

        options = {k: v for k, v in enum.FileAccessMode.__dict__.items() if not k.startswith('_')}
        permission = options.get(acl_entry.perm)
        if permission is not None:
            ace.permissions.allowedFileAccess = permission
        else:
            raise InputError('Invalid permission', acl_entry.perm, list(options.keys()))

        acls.append(ace)

        return acls

    @staticmethod
    def _validate_acl(acl):
        if not isinstance(acl, list):
            raise InputError('Invalid access control list format', repr(acl), '[("type", "name", "perm"), ...]')
        for acl_entry in acl:
            if not isinstance(acl_entry, ShareAccessControlEntry):
                raise InputError('Invalid access control entry format', repr(acl_entry), 'cterasdk.edge.types.ShareAccessControlEntry')

    @staticmethod
    def _validate_remove_acl(acl):
        if not isinstance(acl, list):
            raise InputError('Invalid access control list format', repr(acl), '[("type", "name", "perm"), ...]')
        for acl_entry in acl:
            if not isinstance(acl_entry, RemoveShareAccessControlEntry):
                raise InputError(
                    'Invalid access control entry format',
                    repr(acl_entry),
                    'cterasdk.edge.types.RemoveShareAccessControlEntry'
                )
