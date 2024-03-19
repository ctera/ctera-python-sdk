from ...common import Object


class Event(Object):
    """
    :ivar str type: Object type
    :ivar str guid: Object Unique Identifier (GUID)
    :ivar str gvsn: GVSN
    :ivar int folder_id: Cloud Drive Folder ID
    :ivar bool deleted: Deleted
    :ivar str name: Object Name
    :ivar parent guid: Parent Object Unique Identifier (GUID)
    :ivar datetime.datetime: Last Modified Timestamp
    :ivar int size: Object Size
    """
    def __init__(self, type, guid, folder_id, deleted, name,  # pylint: disable=redefined-builtin
                 modified, size, gvsn=None, parent_guid=None):
        self.type = type
        self.guid = guid
        self.gvsn = gvsn
        self.folder_id = folder_id
        self.deleted = deleted
        self.name = name
        self.modified = modified
        self.size = size
        self.parent_guid = parent_guid

    @staticmethod
    def from_server_object(server_object):
        return Event(**server_object.__dict__)
