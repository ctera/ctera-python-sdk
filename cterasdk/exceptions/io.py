from .base import CTERAException


class StorageError(CTERAException):
    """
    Base Exception for Remote File Storage

    :ivar str message: Error message.
    """
    def __init__(self, message=None, **kwargs):
        super().__init__(message, **kwargs)


class ResourceNotFoundError(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Resource not found. Please verify the path and try again.', **kwargs)


class NotADirectory(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Target validation error: Resource exists but it is not a directory.', **kwargs)


class ResourceExistsError(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Resource already exists: a file or folder with this name already exists.', **kwargs)


class PathValidationError(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Path validation failed: the specified destination path does not exist.', **kwargs)


class NameSyntaxError(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Invalid name: the name contains characters that are not allowed "\\ / : ? & < > \" |".', **kwargs)


class ReservedNameError(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Reserved name error: the name is reserved and cannot be used.', **kwargs)


class RestrictedPathError(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Creating a folder in the specified location is forbidden.', **kwargs)


class RestrictedRoot(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Storing files to the root directory is forbidden.', **kwargs)


class PermissionDenied(StorageError):

    def __init__(self, **kwargs):
        super().__init__('Permission denied: Inappropriate permissions to access this resource.', **kwargs)


class UnwriteableScope(StorageError):

    def __init__(self, **kwargs):
        super().__init__("Write access denied. This target is protected and cannot be modified.", **kwargs)


class FileConflict(StorageError):

    def __init__(self, cursor):
        super().__init__('Conflict: a file with the same name already exists.')
        self.cursor = cursor


class UploadException(StorageError):
    """
    Upload Exception

    :ivar str path: Path
    """
    def __init__(self, message, path):
        super().__init__(f'Upload failed: {message}.', path=path)


class QuotaViolation(UploadException):

    def __init__(self, entity, path):
        super().__init__(f'{entity} is out of quota', path=path)


class RejectedByPolicy(UploadException):

    def __init__(self, path):
        super().__init__('Rejected by Cloud Drive policy rule', path=path)


class NoStorageBucket(UploadException):

    def __init__(self, path):
        super().__init__('No available storage location', path=path)


class WindowsACLError(UploadException):

    def __init__(self, path):
        super().__init__('Unable to store file in a Windows ACL-enabled cloud folder', path=path)
