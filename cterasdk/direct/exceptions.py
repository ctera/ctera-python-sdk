import errno


class DirectIOError(IOError):
    """Base Exception for Direct IO Errors"""


class StreamError(DirectIOError):

    def __init__(self, filename, offset):
        super().__init__(errno.EIO, 'Failed to stream file', filename)
        self.offset = offset


class DirectIOAPIError(DirectIOError):
    """Direct IO API Error"""

    def __init__(self, error, strerror, filename):
        super().__init__(error, strerror, filename)


class NotFoundError(DirectIOAPIError):

    def __init__(self, filename):
        super().__init__(errno.EBADF, 'File not found', filename)


class UnAuthorized(DirectIOAPIError):

    def __init__(self, filename):
        super().__init__(errno.EACCES, 'Unauthorized: You do not have the necessary permissions to access this resource', filename)


class UnprocessableContent(DirectIOAPIError):

    def __init__(self, filename):
        super().__init__(errno.ENOTSUP, 'Not all blocks of the requested file are stored on a storage node set to Direct Mode', filename)


class BlocksNotFoundError(DirectIOAPIError):

    def __init__(self, filename):
        super().__init__(errno.ENODATA, 'Blocks not found', filename)


class BlockListConnectionError(DirectIOAPIError):

    def __init__(self, filename):
        super().__init__(errno.ENETRESET, 'Failed to list blocks. Connection error', filename)


class BlockListTimeout(DirectIOAPIError):

    def __init__(self, filename):
        super().__init__(errno.ETIMEDOUT, 'Failed to list blocks. Timed out', filename)


class DecryptKeyError(DirectIOError):

    def __init__(self, filename):
        super().__init__(errno.EIO, 'Failed to decrypt secret key', filename)


class BlockInfo:

    def __init__(self, chunk):
        """
        Initialize an Block Info Object for Direct IO Error Object.

        :param cterasdk.direct.types.Chunk chunk: Chunk.
        """
        self.file_id = chunk.file_id
        self.number = chunk.index
        self.offset = chunk.offset
        self.length = chunk.length


class BlockError(DirectIOError):
    """Direct IO Block Error"""

    def __init__(self, error, strerror, chunk):
        super().__init__(error, strerror, chunk.file_id)
        self.block = BlockInfo(chunk)


class DownloadError(BlockError):

    def __init__(self, strerror, chunk):
        super().__init__(errno.EIO, strerror, chunk)


class DownloadTimeout(BlockError):

    def __init__(self, chunk):
        super().__init__(errno.ETIMEDOUT, 'Failed to download block. Timed out', chunk)


class DownloadConnectionError(BlockError):

    def __init__(self, chunk):
        super().__init__(errno.ENETRESET, 'Failed to download block. Connection error', chunk)


class DecryptBlockError(BlockError):

    def __init__(self, chunk):
        super().__init__(errno.EIO, 'Failed to decrypt block', chunk)


class DecompressBlockError(BlockError):

    def __init__(self, chunk):
        super().__init__(errno.EIO, 'Failed to decompress block', chunk)


class BlockValidationException(BlockError):

    def __init__(self, chunk):
        super().__init__(errno.EIO, 'Expected block length does not match decrypted and decompressed block length', chunk)
