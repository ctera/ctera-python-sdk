import errno
from .base import BaseIOError


EREMOTEIO = 121


class FileExistsError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EEXIST, 'File exists', filename)


class ObjectNotFoundError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.ENOENT, 'Object not found', filename)


class FileNotFoundError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.ENOENT, 'File not found', filename)


class FolderNotFoundError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.ENOENT, 'Folder not found', filename)


class NotADirectoryError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.ENOTDIR, 'Not a directory', filename)


class WriteError(BaseIOError):

    def __init__(self, strerror, filename):
        super().__init__(EREMOTEIO, f'Write failed. Reason: {strerror}', filename)


class ROFSError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EROFS, 'Write access denied. Target path is read-only', filename)


class PrivilegeError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EACCES, 'Access denied. No permission to access resource', filename)


class NTACLError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EACCES, 'Access denied. Unable to access Windows ACL-enabled volume', filename)


class QuotaError(BaseIOError):

    def __init__(self, filename):
        super().__init__(errno.EDQUOT, 'Write failed. Out of quota', filename)


class StorageBackendError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Storage backend unavailable', filename)


class FileRejectedError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Rejected by policy', filename)


class FilenameError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'File name contains characters that are not allowed "\\ / : ? & < > \" |".', filename)


class ReservedNameError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Specified name is reserved by the system', filename)


class GetSnapshotsError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to enumerate versions', filename)


class CreateDirectoryError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to create folder', filename)


class GetShareMetadataError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to retrieve collaboration-share metadata', filename)


class CreateLinkError(BaseIOError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to create public link', filename)