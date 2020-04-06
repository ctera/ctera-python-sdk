from . import enum
from ..common import Object
from ..exception import InputError


class UserGroupEntry():
    """
    User or Group Entry

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    """

    _valid_principal_types = list({k: v for k, v in enum.PrincipalType.__dict__.items() if not k.startswith('_')}.values())

    def __init__(self, principal_type, name):
        UserGroupEntry._validate_principal_type(principal_type)
        self._principal_type = principal_type
        self.name = name

    @property
    def principal_type(self):
        return self._principal_type

    @principal_type.setter
    def principal_type(self, principal_type):
        UserGroupEntry._validate_principal_type(principal_type)
        self._principal_type = principal_type

    def to_server_object(self):
        user_group_obj = Object()
        if self.principal_type == enum.PrincipalType.LU:
            user_group_obj._classname = enum.PrincipalType.LU  # pylint: disable=protected-access
            user_group_obj.ref = "#config#auth#users#" + self.name
        elif self.principal_type == enum.PrincipalType.LG:
            user_group_obj._classname = enum.PrincipalType.LG  # pylint: disable=protected-access
            user_group_obj.ref = "#config#auth#groups#" + self.name
        elif self.principal_type == enum.PrincipalType.DU:
            user_group_obj._classname = enum.PrincipalType.DU  # pylint: disable=protected-access
            user_group_obj.name = self.name
        elif self.principal_type == enum.PrincipalType.DG:
            user_group_obj._classname = enum.PrincipalType.DG  # pylint: disable=protected-access
            user_group_obj.name = self.name
        return user_group_obj

    @staticmethod
    def from_server_object(server_object):
        principal_type = server_object._classname  # pylint: disable=protected-access
        if principal_type in [enum.PrincipalType.LU, enum.PrincipalType.LG]:
            name = server_object.ref
            name = name[name.rfind('#') + 1:]
        else:
            name = server_object.name
        return UserGroupEntry(principal_type, name)

    @staticmethod
    def _validate_principal_type(principal_type):
        if principal_type not in UserGroupEntry._valid_principal_types:
            raise InputError('Invalid principal type', principal_type, UserGroupEntry._valid_principal_types)


class ShareAccessControlEntry():
    """
    Share access control entry for filer shares

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    :ivar cterasdk.edge.enum.FileAccessMode perm: The file access permission
    """

    _valid_permissions = list({k: v for k, v in enum.FileAccessMode.__dict__.items() if not k.startswith('_')}.values())

    def __init__(self, principal_type, name, perm):
        ShareAccessControlEntry._validate_permission(perm)
        self._user_group_entry = UserGroupEntry(principal_type, name)
        self._perm = perm

    @property
    def principal_type(self):
        return self._user_group_entry.principal_type

    @principal_type.setter
    def principal_type(self, principal_type):
        self._user_group_entry.principal_type = principal_type

    @property
    def name(self):
        return self._user_group_entry.name

    @name.setter
    def name(self, name):
        self._user_group_entry.name = name

    @property
    def perm(self):
        return self._perm

    @perm.setter
    def perm(self, perm):
        ShareAccessControlEntry._validate_permission(perm)
        self._perm = perm

    def to_server_object(self):
        ace = Object()
        ace._classname = "ShareACLRule"  # pylint: disable=protected-access
        ace.principal2 = self._user_group_entry.to_server_object()
        ace.permissions = self._create_permissions_object()
        return ace

    def _create_permissions_object(self):
        permissions = Object()
        permissions._classname = "FileAccessPermissions"  # pylint: disable=protected-access
        permissions.allowedFileAccess = self.perm
        return permissions

    @staticmethod
    def from_server_object(server_object):
        user_group_entry = UserGroupEntry.from_server_object(server_object.principal2)
        perm = server_object.permissions.allowedFileAccess
        return ShareAccessControlEntry(user_group_entry.principal_type, user_group_entry.name, perm)

    @staticmethod
    def _validate_permission(permission):
        if permission not in ShareAccessControlEntry._valid_permissions:
            raise InputError('Invalid permissions', permission, ShareAccessControlEntry._valid_permissions)


class RemoveShareAccessControlEntry(UserGroupEntry):
    """
    Object holding share access control principal type and name

    :ivar cterasdk.edge.enum.PrincipalType principal_type: Principal type of the ACL
    :ivar str name: The name of the user or group
    """
