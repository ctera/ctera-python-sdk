from .base import CTERAException


class RemoteStorageException(CTERAException):
    """
    Base Exception for Remote File Storage

    :ivar str path: Path
    """
    def __init__(self, message, path):
        super().__init__(message)
        self.path = path


class ResourceNotFoundError(RemoteStorageException):

    def __init__(self, path):
        super().__init__('Remote directory not found. Please verify the path and try again.', path)


class NotADirectory(RemoteStorageException):

    def __init__(self, path):
        super().__init__('Target validation error: Resource exists but it is not a directory.', path)


class ResourceExistsError(CTERAException):

    def __init__(self):
        super().__init__('Resource already exists: a file or folder with this name already exists.')


class PathValidationError(CTERAException):

    def __init__(self):
        super().__init__('Path validation failed: the specified destination path does not exist.')


class NameSyntaxError(CTERAException):

    def __init__(self):
        super().__init__('Invalid name: the name contains characters that are not allowed.')


class ReservedNameError(CTERAException):

    def __init__(self):
        super().__init__('Reserved name error: the name is reserved and cannot be used.')


class RestrictedPathError(CTERAException):

    def __init__(self):
        super().__init__('Creating a folder in the specified location is forbidden.')
