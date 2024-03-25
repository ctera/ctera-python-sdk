from ...common import Object


class Event(Object):  # pylint: disable=too-many-instance-attributes
    """
    :ivar str type: Object type
    :ivar str guid: Object Unique Identifier (GUID)
    :ivar int folder_id: Cloud Drive Folder ID
    :ivar bool deleted: Deleted
    :ivar str name: Object Name
    :ivar str modified: Last Modified Timestamp (ISO 8601)
    :ivar int size: Object Size
    :ivar int,optional id: File ID
    :ivar str,optional acl: ACL SDDL
    :ivar str,optional gvsn: GVSN
    :ivar str,optional parent_guid: Parent Object Unique Identifier (GUID)
    """
    def __init__(self, type, guid, folder_id, deleted, name,  # pylint: disable=redefined-builtin, too-many-arguments
                 modified, size, id=None, acl=None, gvsn=None, parent_guid=None):  # pylint: disable=redefined-builtin
        self.type = type
        self.guid = guid
        self.folder_id = folder_id
        self.deleted = deleted
        self.name = name
        self.modified = modified
        self.size = size
        self.id = id
        self.acl = acl
        self.gvsn = gvsn
        self.parent_guid = parent_guid

    @staticmethod
    def from_server_object(server_object):
        return Event(**server_object.__dict__)
