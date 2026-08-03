import re
from .base import CTERAException


class BaseNotificationsError(CTERAException):
    """
    Base Notifications Rrror

    :ivar list[int] cloudfolders: List of cloudfolders
    """
    def __init__(self, strerror, cloudfolders):
        super().__init__(strerror)
        self.cloudfolders = cloudfolders


class TooManyVolumesRequestedError(BaseNotificationsError):
    """
    Raised when the number of volumes requested is outside the allowed range.

    :ivar int min_size: Min allowed number of cloudfolders.
    :ivar int max_size: Max allowed number of cloudfolders.
    """

    def __init__(self, cloudfolders, message):
        match = re.search(r"between\s+(\d+)\s+and\s+(\d+)", message)
        if match is None:
            raise ValueError(f"Could not parse error from message: {message}")

        min_size, max_size = match.group(1), match.group(2)

        super().__init__(f"Too many cloudfolders requested: {len(cloudfolders)} requested, but only {max_size} are allowed", cloudfolders)

        self.min_size = min_size
        self.max_size = max_size


class NotificationsError(BaseNotificationsError):
    """
    Notifications error

    :ivar list[int] cloudfolders: List of cloudfolders
    :ivar str cursor: Cursor
    """

    def __init__(self, cloudfolders, cursor):
        super().__init__('An error occurred while trying to retrieve notifications.', cloudfolders)
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
