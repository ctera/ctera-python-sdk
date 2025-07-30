from .base import CTERAException


class AuthenticationError(CTERAException):
    """
    Exception raised for authentication failures.
    """

    def __init__(self):
        super().__init__("Authentication failed: Invalid username or password")
