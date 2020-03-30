from . import enum
from ..common import Object
from ..exception import InputError


class ShareAccessControlEntryBase():
    _valid_principal_types = list({k: v for k, v in enum.PrincipalType.__dict__.items() if not k.startswith('_')}.values())

    def __init__(self, principal_type, name):
        if principal_type not in ShareAccessControlEntry._valid_principal_types:
            raise InputError('Invalid principal type', principal_type, self._valid_principal_types)
        self.principal_type = principal_type
        self.name = name

    def _create_principal2_object(self):
        principal2 = Object()
        if self.principal_type == enum.PrincipalType.LU:
            principal2._classname = enum.PrincipalType.LU  # pylint: disable=protected-access
            principal2.ref = "#config#auth#users#" + self.name
        elif self.principal_type == enum.PrincipalType.LG:
            principal2._classname = enum.PrincipalType.LG  # pylint: disable=protected-access
            principal2.ref = "#config#auth#groups#" + self.name
        elif self.principal_type == enum.PrincipalType.DU:
            principal2._classname = enum.PrincipalType.DU  # pylint: disable=protected-access
            principal2.name = self.name
        elif self.principal_type == enum.PrincipalType.DG:
            principal2._classname = enum.PrincipalType.DG  # pylint: disable=protected-access
            principal2.name = self.name
        return principal2


class ShareAccessControlEntry(ShareAccessControlEntryBase):
    """
    Share access control entry for filer shares

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    :ivar cterasdk.edge.enum.FileAccessMode perm: The file access permission
    """

    _valid_permissions = list({k: v for k, v in enum.FileAccessMode.__dict__.items() if not k.startswith('_')}.values())

    def __init__(self, principal_type, name, perm):
        super().__init__(principal_type=principal_type, name=name)
        if perm not in ShareAccessControlEntry._valid_permissions:
            raise InputError('Invalid permissions', perm, ShareAccessControlEntry._valid_permissions)
        self.perm = perm

    def to_server_object(self):
        ace = Object()
        ace._classname = "ShareACLRule"  # pylint: disable=protected-access
        ace.principal2 = self._create_principal2_object()
        ace.permissions = self._create_permissions_object()
        return ace

    def _create_permissions_object(self):
        permissions = Object()
        permissions._classname = "FileAccessPermissions"  # pylint: disable=protected-access
        permissions.allowedFileAccess = self.perm
        return permissions

    @staticmethod
    def from_server_object(server_object):
        principal_type = server_object.principal2._classname  # pylint: disable=protected-access
        if principal_type in [enum.PrincipalType.LU, enum.PrincipalType.LG]:
            name = server_object.principal2.ref
            name = name[name.rfind('#') + 1:]
        else:
            name = server_object.principal2.name
        perm = server_object.permissions.allowedFileAccess
        return ShareAccessControlEntry(principal_type, name, perm)


class RemoveShareAccessControlEntry(ShareAccessControlEntryBase):
    """
    Object holding share access control principal type and name

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    """
