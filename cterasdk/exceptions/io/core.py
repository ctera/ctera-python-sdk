import errno
from .base import BaseIOError, PathError, EREMOTEIO


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


class NotADirectoryException(PathError):

    def __init__(self, filename):
        super().__init__(errno.ENOTDIR, 'Not a directory', filename)


class OpenError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to open file', filename)


class UploadError(PathError):

    def __init__(self, strerror, filename):
        super().__init__(EREMOTEIO, f'Upload failed. Reason: {strerror}', filename)


class ROFSError(PathError):

    def __init__(self, filename):
        super().__init__(errno.EROFS, 'Write access denied. Target path is read-only', filename)


class PrivilegeError(PathError):

    def __init__(self, filename):
        super().__init__(errno.EACCES, 'Access denied. No permission to access resource', filename)


class NTACLError(PathError):

    def __init__(self, filename):
        super().__init__(errno.EACCES, 'Access denied. Unable to access Windows ACL-enabled volume', filename)


class QuotaError(PathError):

    def __init__(self, filename):
        super().__init__(errno.EDQUOT, 'Write failed. Out of quota', filename)


class StorageBackendError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Storage backend unavailable', filename)


class FileRejectedError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Rejected by policy', filename)


class FilenameError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'File name contains characters that are not allowed "\\ / : ? & < > \" |".', filename)


class ReservedNameError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Specified name is reserved by the system', filename)


class ListDirectoryError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to list directory', filename)


class GetVersionsError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to enumerate versions', filename)


class CreateDirectoryError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to create folder', filename)


class GetMetadataError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to retrieve object metadata', filename)


class GetShareMetadataError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to retrieve collaboration-share metadata', filename)


class CreateLinkError(PathError):

    def __init__(self, filename):
        super().__init__(EREMOTEIO, 'Failed to create public link', filename)


class RenameError(PathError):

    def __init__(self, paths, cursor):
        source, destination = paths[0]
        super().__init__(EREMOTEIO, 'Failed to rename object', str(source), str(destination.name))
        self.cursor = cursor


class BatchError(BaseIOError):
    """Task Error"""

    def __init__(self, strerror, paths, cursor):
        super().__init__(EREMOTEIO, strerror)
        self.paths = paths
        self.cursor = cursor


class DeleteError(BatchError):

    def __init__(self, paths, cursor):
        super().__init__('Delete error', paths, cursor)


class RecoverError(BatchError):

    def __init__(self, paths, cursor):
        super().__init__('Recover error', paths, cursor)


class CopyError(BatchError):

    def __init__(self, paths, cursor):
        super().__init__('Copy error', paths, cursor)


class MoveError(BatchError):

    def __init__(self, paths, cursor):
        super().__init__('Move error', paths, cursor)
