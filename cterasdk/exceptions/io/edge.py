import errno
from .base import PathError, EREMOTEIO


class FileConflictError(PathError):

    def __init__(self, filename):
        super().__init__(errno.EEXIST, 'File exists', filename)


class ObjectNotFoundError(PathError):

    def __init__(self, filename):
        super().__init__(errno.ENOENT, 'Object not found', filename)


class FileNotFoundException(PathError):

    def __init__(self, filename):
        super().__init__(errno.ENOENT, 'File not found', filename)


class FolderNotFoundError(PathError):

    def __init__(self, filename):
        super().__init__(errno.ENOENT, 'Folder not found', filename)


class GetMetadataError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to retrieve object metadata', filename)


class NotADirectoryException(PathError):

    def __init__(self, filename):
        super().__init__(errno.ENOTDIR, 'Not a directory', filename)


class ROFSError(PathError):

    def __init__(self, filename):
        super().__init__(errno.EROFS, 'Write access denied. Target path is read-only', filename)


class ListDirectoryError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to list directory', filename)


class CreateDirectoryError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to create directory', filename)


class OpenError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to open file', filename)


class DeleteError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to delete object', filename)


class RenameError(PathError):

    def __init__(self, filename, filename2):
        super().__init__(EREMOTEIO, 'Failed to rename object', filename, filename2)


class CopyError(PathError):
    """
    Copy Error.

    :ivar str path: Path
    :ivar str destination: Destination
    """
    def __init__(self, path, destination):
        super().__init__(EREMOTEIO, 'Failed to copy object', path, destination)
        self.destination = destination


class MoveError(PathError):
    """
    Move Error.

    :ivar str path: Path
    :ivar str destination: Destination
    """
    def __init__(self, path, destination):
        super().__init__(EREMOTEIO, 'Failed to move object', path, destination)
        self.destination = destination


class UploadError(PathError):

    def __init__(self, strerror, filename):
        super().__init__(EREMOTEIO, f'Upload failed. Reason: {strerror}', filename)
