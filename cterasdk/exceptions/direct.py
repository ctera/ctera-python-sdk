import errno


class DirectIOError(IOError):
    """Base Exception for Direct IO Errors"""


class StreamError(DirectIOError):
    """
    Stream Error

    :ivar int offset: Stream offset
    """

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
        super().__init__(errno.ENODATA, f'Could not find blocks for file ID: {filename}', filename)


class BlockListConnectionError(DirectIOAPIError):

    def __init__(self, filename):
        super().__init__(errno.ENETRESET, f'Failed to list blocks for file ID: {filename} due to a connection error', filename)


class BlockListTimeout(DirectIOAPIError):

    def __init__(self, filename):
        super().__init__(errno.ETIMEDOUT, f'Timed out while listing blocks for file ID: {filename}', filename)


class DecryptKeyError(DirectIOError):

    def __init__(self, filename):
        super().__init__(errno.EIO, 'Failed to decrypt secret key', filename)


class BlockError(DirectIOError):
    """
    Direct IO Block Error

    :ivar cterasdk.direct.exceptions.BlockInfo block: Block info
    """
    def __init__(self, error, strerror, file_id, chunk):
        super().__init__(error, strerror, file_id)
        self.block = BlockInfo(file_id, chunk)


class DownloadError(BlockError):

    def __init__(self, strerror, file_id, chunk):
        super().__init__(errno.EIO, strerror, file_id, chunk)


class DownloadTimeout(BlockError):

    def __init__(self, file_id, chunk):
        super().__init__(errno.ETIMEDOUT, 'Failed to download block. Timed out', file_id, chunk)


class DownloadConnectionError(BlockError):

    def __init__(self, file_id, chunk):
        super().__init__(errno.ENETRESET, 'Failed to download block. Connection error', file_id, chunk)


class DecryptBlockError(BlockError):

    def __init__(self, file_id, chunk):
        super().__init__(errno.EIO, 'Failed to decrypt block', file_id, chunk)


class DecompressBlockError(BlockError):

    def __init__(self, file_id, chunk):
        super().__init__(errno.EIO, 'Failed to decompress block', file_id, chunk)


class BlockValidationException(BlockError):

    def __init__(self, file_id, chunk):
        super().__init__(errno.EIO, 'Expected block length does not match decrypted and decompressed block length', file_id, chunk)


class BlockInfo:
    """
    Block Info

    :ivar int file_id: File ID
    :ivar int number: Block number
    :ivar int offset: Block offset
    :ivar int length: Block length
    """
    def __init__(self, file_id, chunk):
        """
        Initialize an Block Info Object for Direct IO Error Object.

        :param cterasdk.direct.types.Chunk chunk: Chunk.
        """
        self.file_id = file_id
        self.number = chunk.index
        self.offset = chunk.offset
        self.length = chunk.length
