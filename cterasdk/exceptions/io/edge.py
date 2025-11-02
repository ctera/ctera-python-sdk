import errno
from .base import BaseIOError, EREMOTEIO


class FileConflictError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EEXIST, 'File exists', filename)


class FileNotFoundException(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.ENOENT, 'File not found', filename)


class NotADirectoryException(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.ENOTDIR, 'Not a directory', filename)


class ROFSError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EROFS, 'Write access denied. Target path is read-only', filename)


class CreateDirectoryError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to create directory', filename)
