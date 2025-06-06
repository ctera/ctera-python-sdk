from .base import CTERAException


class SessionExpired(CTERAException):
    """Session expiration"""

    def __init__(self):
        super().__init__('Authentication error: Session expired.')


class NotLoggedIn(CTERAException):
    """No session"""

    def __init__(self):
        super().__init__('Authentication error: Not logged in.')


class ContextError(CTERAException):
    """API invocation context rrror"""

    def __init__(self, message):
        super().__init__(f'Context error: {message}.')
