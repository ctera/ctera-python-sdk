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
