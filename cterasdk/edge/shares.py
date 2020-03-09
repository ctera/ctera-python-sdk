from collections import namedtuple
import logging

from . import enum
from .files import path
from ..common import Object
from ..exception import CTERAException, InputError
from .base_command import BaseCommand


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
        :param list[ShareAccessControlEntry] acl: a list of 3-tuple access control entries
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
        for entry in acl:
            if len(entry) != 3:
                Shares._invalid_ace(entry)
            Shares._add_share_acl_rule(param.acl, entry[0], entry[1], entry[2])

        try:
            self._gateway.add('/config/fileservices/share', param)
            logging.getLogger().info("Share created. %s", {'name': name})
        except Exception as error:
            logging.getLogger().error("Share creation failed.")
            raise CTERAException('Share creation failed', error)

    def set_acl(self, name, acl):
        """
        Set a network share's access control entries.

        :param str name: The share name
        :param list[ShareAccessControlEntry] acl: List of access control entries

        .. warning: this method will override the existing access control entries
        """
        Shares._validate_acl(acl)

        param = []
        for entry in acl:
            if len(entry) != 3:
                Shares._invalid_ace(entry)
            Shares._add_share_acl_rule(param, entry[0], entry[1], entry[2])
        self._gateway.put('/config/fileservices/share/' + name + '/acl', param)

    def add_acl(self, name, acl):
        """
        Add one or more access control entries to an existing share.

        :param str name: The share name
        :param list[ShareAccessControlEntry] acl: List of access control entries to add
        """
        Shares._validate_acl(acl)

        current_acl = self._gateway.get('/config/fileservices/share/' + name + '/acl')

        new_acl_dict = {}
        for entry in acl:
            temp_acl = []
            if len(entry) != 3:
                Shares._invalid_ace(entry)
            Shares._add_share_acl_rule(temp_acl, entry[0], entry[1], entry[2])
            entry_key = entry[0] + '#' + entry[1]
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

        acl = [v for k, v in new_acl_dict.items()]
        self._gateway.put('/config/fileservices/share/' + name + '/acl', acl)

    def remove_acl(self, name, tuples):
        """
        Remove one or more access control entries from an existing share.

        :param str name: The share name
        :param list[RemoveShareAccessControlEntry] acl: List of access control entries to remove
        """
        if not isinstance(tuples, list):
            raise InputError('Invalid input', repr(tuples), '[("type", "name"), ...]')

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

            if (options.get(ace_type), ace_name) not in tuples:
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
    def _add_share_acl_rule(acls, principal_type_field, name, perm):
        ace = Object()
        ace._classname = "ShareACLRule"  # pylint: disable=protected-access
        ace.principal2 = Object()

        options = {k: v for k, v in enum.PrincipalType.__dict__.items() if not k.startswith('_')}
        principal_type = options.get(principal_type_field)
        if principal_type == enum.PrincipalType.LU:
            ace.principal2._classname = enum.PrincipalType.LU  # pylint: disable=protected-access
            ace.principal2.ref = "#config#auth#users#" + name
        elif principal_type == enum.PrincipalType.LG:
            ace.principal2._classname = enum.PrincipalType.LG  # pylint: disable=protected-access
            ace.principal2.ref = "#config#auth#groups#" + name
        elif principal_type == enum.PrincipalType.DU:
            ace.principal2._classname = enum.PrincipalType.DU  # pylint: disable=protected-access
            ace.principal2.name = name
        elif principal_type == enum.PrincipalType.DG:
            ace.principal2._classname = enum.PrincipalType.DG  # pylint: disable=protected-access
            ace.principal2.name = name
        else:
            raise InputError('Invalid principal type', principal_type_field, list(options.keys()))

        ace.permissions = Object()
        ace.permissions._classname = "FileAccessPermissions"  # pylint: disable=protected-access

        options = {k: v for k, v in enum.FileAccessMode.__dict__.items() if not k.startswith('_')}
        permission = options.get(perm)
        if permission is not None:
            ace.permissions.allowedFileAccess = permission
        else:
            raise InputError('Invalid permission', perm, list(options.keys()))

        acls.append(ace)

        return acls

    @staticmethod
    def _validate_acl(acl):
        if not isinstance(acl, list):
            raise InputError('Invalid access control list format', repr(acl), '[("type", "name", "perm"), ...]')

    @staticmethod
    def _invalid_ace(entry):
        raise InputError('Invalid input', repr(entry), '[("type", "name", "perm"), ...]')


ShareAccessControlEntry = namedtuple('ShareAccessControlEntry', ('type', 'name', 'perm'))
ShareAccessControlEntry.__doc__ = 'Tuple holding the principal type, name and permission'
ShareAccessControlEntry.type.__doc__ = 'The principal type'
ShareAccessControlEntry.name.__doc__ = 'The name of the user or group'
ShareAccessControlEntry.perm.__doc__ = 'The file access permission'

RemoveShareAccessControlEntry = namedtuple('RemoveShareAccessControlEntry', ('type', 'name'))
RemoveShareAccessControlEntry.__doc__ = 'Tuple holding the principal type and name'
RemoveShareAccessControlEntry.type.__doc__ = 'The principal type'
RemoveShareAccessControlEntry.name.__doc__ = 'The name of the user or group'
