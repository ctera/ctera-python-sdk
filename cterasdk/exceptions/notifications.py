from .base import CTERAException


class NotificationsError(CTERAException):
    """
    Notifications error

    :ivar list[int] cloudfolders: List of cloudfolders
    :ivar str cursor: Cursor
    """

    def __init__(self, cloudfolders, cursor):
        super().__init__('An error occurred while trying to retrieve notifications.')
        self.cloudfolders = cloudfolders
        self.cursor = cursor


class AncestorsError(CTERAException):
    """
    Ancestors Error

    :ivar int folder_id: Cloud Drive folder unique identifer
    :ivar str guid: File GUID
    """
    def __init__(self, folder_id, guid):
        super().__init__(f'Could not retrieve ancestors for: {folder_id}:{guid}')
        self.folder_id = folder_id
        self.guid = guid
