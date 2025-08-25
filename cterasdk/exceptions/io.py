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

    def __init__(self):
        super().__init__('Resource already exists: a file or folder with this name already exists.')


class PathValidationError(RemoteStorageError):

    def __init__(self):
        super().__init__('Path validation failed: the specified destination path does not exist.')


class NameSyntaxError(RemoteStorageError):

    def __init__(self, path):
        super().__init__('Invalid name: the name contains characters that are not allowed "\\ / : ? & < > \" |".', path)


class ReservedNameError(RemoteStorageError):

    def __init__(self):
        super().__init__('Reserved name error: the name is reserved and cannot be used.')


class RestrictedPathError(RemoteStorageError):

    def __init__(self):
        super().__init__('Creating a folder in the specified location is forbidden.')


class RestrictedRoot(RemoteStorageError):

    def __init__(self):
        super().__init__('Storing files to the root directory is forbidden.', '/')


class InsufficientPermission(RemoteStorageError):

    def __init__(self):
        super().__init__('Permission denied: You must have appropriate permissions to access this resource.')


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
