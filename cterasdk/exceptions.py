from .common import Object
from .convert import tojsonstr


class CTERAException(Exception):

    def __init__(self, message=None, instance=None, **kwargs):
        super().__init__()
        self.classname = self.__class__.__name__
        self.join(instance)
        if message is not None:
            self.message = message
        self.put(**kwargs)

    def put(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def join(self, instance=None):
        if instance is not None:
            self.__dict__ = instance.__dict__.copy()

    def __str__(self):
        return tojsonstr(self)


class ContextError(CTERAException):
    """API Invocation Context Error"""


class SessionExpired(CTERAException):
    """Raised on Session Expiration"""

    def __init__(self):
        super().__init__('Session expired.')


class NotLoggedIn(CTERAException):
    """Raised on No Session"""

    def __init__(self):
        super().__init__('Not logged in.')


class ClientResponseException(CTERAException):

    def __init__(self, error_object):
        super().__init__('An error occurred while processing the HTTP request.', error_object)


class NotificationsError(CTERAException):

    def __init__(self, cloudfolders, cursor):
        super().__init__('An error occurred while trying to retrieve notifications.', cloudfolders=cloudfolders, cursor=cursor)


class ObjectNotFoundException(CTERAException):

    def __init__(self, message, object_ref, **kwargs):
        super().__init__(message, None, **kwargs)
        self.response = Object()
        self.response.code = 404
        self.response.reason = 'Not Found'
        self.response.body = Object()
        self.response.body.rc = 1
        self.response.body.msg = f"Object '{object_ref}' not found"


class PythonVersionException(CTERAException):

    def __init__(self, version):
        super().__init__('You are running an unsupported version of Python', None, version=version)


class InputError(CTERAException):

    def __init__(self, message, expression, options):
        CTERAException.__init__(self, message, None, expression=expression, options=options)


class ConsentException(CTERAException):
    """Consent Exception"""
