import errno
from .base import BaseIOError


class FileExistsError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EEXIST, 'File exists', filename)


class FileNotFoundError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.ENOENT, 'File not found', filename)


class NotADirectoryError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.ENOTDIR, 'Not a directory', filename)


class ROFSError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EROFS, 'Write access denied. Target path is read-only', filename)
