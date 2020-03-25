from collections import namedtuple


ShareAccessControlEntry = namedtuple('ShareAccessControlEntry', ('type', 'name', 'perm'))
ShareAccessControlEntry.__doc__ = 'Tuple holding the principal type, name and permission'
ShareAccessControlEntry.type.__doc__ = 'The principal type'
ShareAccessControlEntry.name.__doc__ = 'The name of the user or group'
ShareAccessControlEntry.perm.__doc__ = 'The file access permission'


RemoveShareAccessControlEntry = namedtuple('RemoveShareAccessControlEntry', ('type', 'name'))
RemoveShareAccessControlEntry.__doc__ = 'Tuple holding the principal type and name'
RemoveShareAccessControlEntry.type.__doc__ = 'The principal type'
RemoveShareAccessControlEntry.name.__doc__ = 'The name of the user or group'
