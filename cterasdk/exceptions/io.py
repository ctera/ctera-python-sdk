from .base import CTERAException


class RemoteStorageError(CTERAException):
    """
    Base Exception for Remote File Storage

    :ivar str path: Path
    """
    def __init__(self, message, path=None):
        super().__init__(message)
        self.path = path


class ResourceNotFoundError(RemoteStorageError):

    def __init__(self, path):
        super().__init__('Remote directory not found. Please verify the path and try again.', path)


class NotADirectory(RemoteStorageError):

    def __init__(self, path):
        super().__init__('Target validation error: Resource exists but it is not a directory.', path)


class ResourceExistsError(RemoteStorageError):

    def __init__(self, path):
        super().__init__('Resource already exists: a file or folder with this name already exists.', path)


class PathValidationError(RemoteStorageError):

    def __init__(self, path=None, **kwargs):  # pylint: disable=unused-argument
        super().__init__('Path validation failed: the specified destination path does not exist.', path)


class NameSyntaxError(RemoteStorageError):

    def __init__(self, path):
        super().__init__('Invalid name: the name contains characters that are not allowed "\\ / : ? & < > \" |".', path)


class ReservedNameError(RemoteStorageError):

    def __init__(self, path):
        super().__init__('Reserved name error: the name is reserved and cannot be used.', path)


class RestrictedPathError(RemoteStorageError):

    def __init__(self, path):
        super().__init__('Creating a folder in the specified location is forbidden.', path)


class RestrictedRoot(RemoteStorageError):

    def __init__(self):
        super().__init__('Storing files to the root directory is forbidden.', '/')


class PermissionDenied(RemoteStorageError):

    def __init__(self, action, path=None):
        super().__init__('Permission denied: Inappropriate permissions to access this resource.', path)
        self.action = action


class UnwriteableScope(RemoteStorageError):

    def __init__(self, path, scope):
        super().__init__("Write access denied. This target is protected and cannot be modified.", path)
        self.scope = scope


class FileConflict(RemoteStorageError):

    def __init__(self, action, name, cursor):
        super().__init__('Conflict: a file with the same name already exists.')
        self.action = action
        self.name = name
        self.cursor = cursor


class UploadException(RemoteStorageError):
    """
    Upload Exception

    :ivar str path: Path
    """
    def __init__(self, message, path):
        super().__init__(f'Upload failed: {message}.', path)


class OutOfQuota(UploadException):

    def __init__(self, entity, path):
        super().__init__(f'{entity} is out of quota', path)


class RejectedByPolicy(UploadException):

    def __init__(self, path):
        super().__init__('Rejected by Cloud Drive policy rule', path)


class NoStorageBucket(UploadException):

    def __init__(self, path):
        super().__init__('No available storage location', path)


class WindowsACLError(UploadException):

    def __init__(self, path):
        super().__init__('Unable to store file in a Windows ACL-enabled cloud folder', path)
