from ...common import Object


class Event(Object):  # pylint: disable=too-many-instance-attributes
    """
    :ivar str type: Object type
    :ivar str guid: Object Unique Identifier (GUID)
    :ivar bool deleted: Deleted
    :ivar str name: Object Name
    :ivar int,optional folder_id: Cloud Drive Folder ID
    :ivar str,optional file_timestamp: File Timestamp
    :ivar str,optional portal_modified_date: Portal Modified Date
    :ivar str,optional virtual_portal_id: Virtual Portal ID
    :ivar int,optional size: Object Size
    :ivar int,optional id: File ID
    :ivar str,optional acl: ACL SDDL
    :ivar str,optional gvsn: GVSN
    :ivar str,optional parent_guid: Parent Object Unique Identifier (GUID)
    """
    def __init__(  # pylint: disable=redefined-builtin, too-many-arguments
            self, type, guid, deleted, name, folder_id=None, modified=None,
            file_timestamp=None, size=None, id=None, acl=None, gvsn=None,
            parent_guid=None, portal_modified_date=None, virtual_portal_id=None):
        self.type = type
        self.guid = guid
        self.folder_id = folder_id
        self.deleted = deleted
        self.name = name
        self.file_timestamp = file_timestamp
        self.portal_modified_date = portal_modified_date if portal_modified_date is not None else modified
        self.virtual_portal_id = virtual_portal_id
        self.size = size
        self.id = id
        self.acl = acl
        self.gvsn = gvsn
        self.parent_guid = parent_guid

    @staticmethod
    def from_server_object(server_object):
        return Event(**server_object.__dict__)
