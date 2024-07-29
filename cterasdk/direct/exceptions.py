from ..exceptions import CTERAException


class DirectIOError(CTERAException):
    """Base Exception for DirectIO Errors"""


class NotFoundError(DirectIOError):

    def __init__(self, file_id):
        super().__init__('File not found', file_id=file_id)


class UnAuthorized(DirectIOError):

    def __init__(self):
        super().__init__('Unauthorized: You do not have the necessary permissions to access this resource')


class UnprocessableContent(DirectIOError):

    def __init__(self, file_id):
        super().__init__('Not all blocks of the requested file are stored on a storage node set to Direct Mode', file_id=file_id)


class BlocksNotFoundError(DirectIOError):

    def __init__(self, file_id):
        super().__init__('Blocks not found', file_id=file_id)


class DownloadBlockError(DirectIOError):

    def __init__(self, chunk, error):
        super().__init__('Failed to download block', file_id=chunk.file_id, number=chunk.index, offset=chunk.offset, error=error)


class DecryptError(DirectIOError):
    """Base Exception for Decryption Errors"""


class DecryptKeyError(DecryptError):

    def __init__(self):
        super().__init__('Failed to decrypt secret key')


class DecryptBlockError(DecryptError):

    def __init__(self):
        super().__init__('Failed to decrypt block')


class DecompressBlockError(DirectIOError):

    def __init__(self):
        super().__init__('Failed to decompress block')


class BlockValidationException(DirectIOError):

    def __init__(self, **kwargs):
        super().__init__('Expected block length does not match decrypted and decompressed block length', **kwargs)
