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


class ClientResponseException(CTERAException):

    def __init__(self, error_object):
        super().__init__('An error occurred while processing the HTTP request.', error_object)


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


class RemoteFileSystemException(CTERAException):
    pass


class RemoteDirectoryNotFound(RemoteFileSystemException):

    def __init__(self, path):
        super().__init__('Could not find remote directory', None, path=path)


class DirectIOError(CTERAException):
    """Base Exception for DirectIO Errors"""


class NotFoundError(DirectIOError):

    def __init__(self, file_id):
        super().__init__('File not found', None, file_id=file_id)


class BlocksNotFoundError(DirectIOError):

    def __init__(self, file_id):
        super().__init__('Blocks not found', None, file_id=file_id)


class UnAuthorized(DirectIOError):

    def __init__(self):
        super().__init__('Unauthorized: You do not have the necessary permissions to access this resource')


class UnprocessableContent(DirectIOError):

    def __init__(self, file_id):
        super().__init__('Not all blocks of the requested file are stored on a storage node set to Direct Mode', None, file_id=file_id)


class DecryptError(DirectIOError):
    """Base Exception for Decryption Errors"""


class DecryptKeyError(DecryptError):

    def __init__(self):
        super().__init__('Failed to decrypt secret key')


class DecryptBlockError(DecryptError):

    def __init__(self):
        super().__init__('Failed to decrypt block')


class DecompressError(DirectIOError):

    def __init__(self):
        super().__init__('Failed to decompress block')


class BlockError(DirectIOError):
    """Block Error"""

    def __init__(self, file_id, number, error):
        super().__init__('An error occurred while processing a block.', error=error, file_id=file_id, number=number)


class StreamError(DirectIOError):
    """Stream Error"""

    def __init__(self, error):
        super().__init__('An error occurred while processing stream.', error=error)