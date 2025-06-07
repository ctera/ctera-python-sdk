import logging
import asyncio

from .types import Metadata, Block
from .credentials import KeyPair, Bearer
from .crypto import decrypt_key, decrypt_block
from .decompressor import decompress
from ..exceptions.transport import HTTPError
from ..exceptions.direct import (
    UnAuthorized, UnprocessableContent, BlocksNotFoundError, DownloadError, DownloadTimeout, BlockListTimeout,
    DownloadConnectionError, DecryptKeyError, DecryptBlockError, NotFoundError, DecompressBlockError,
    BlockValidationException, BlockListConnectionError, DirectIOError
)


logger = logging.getLogger('cterasdk.direct')


async def retry(coro, retries=3, backoff=1):
    """
    Retry Coroutine.

    :param coroutine coro: Asynchronous Coroutine.
    :param int retries: Retries.
    :param int backoff: Seconds.
    """
    attempts = 0
    while attempts < retries:
        try:
            return await coro()
        except DirectIOError as error:
            attempts = attempts + 1
            if attempts == retries:
                raise error
            wait = backoff * (2 ** (attempts - 1))
            logger.debug('Download of block failed on attempt %s. Retrying in %s seconds...', attempts, wait)
            await asyncio.sleep(wait)


async def get_object(client, file_id, chunk):
    """
    Get Object from a Signed URL.

    :param int file_id: File ID.
    :param cterasdk.direct.types.Chunk chunk: Chunk.
    :returns: Object
    :rtype: bytes
    """
    async def get_object_coro():

        message = (
            f"Downloading block #{chunk.index} "
            f"(offset={chunk.offset}, length={chunk.length})"
        )

        if file_id:
            message += f" for file ID {file_id}"

        error_message, exception = None, None

        logger.debug(message)
        try:
            response = await client.get(chunk.url)
            return await response.read()
        except ConnectionError:
            error_message = 'connection'
            exception = DownloadConnectionError(file_id, chunk)
        except asyncio.TimeoutError:
            error_message = 'timeout'
            exception = DownloadTimeout(file_id, chunk)
        except IOError as error:
            error_message = 'io'
            exception = DownloadError(error, file_id, chunk)
        except HTTPError as error:
            error_message = 'unknown'
            exception = DownloadError(error.error, file_id, chunk)

        error_messages = {
            "connection": "Connection error",
            "timeout": "Timed out",
            "io": "I/O error",
            "unknown": "Unknown error"
        }

        message = (
            f"Failed to download block #{chunk.index} "
            f"(offset={chunk.offset}, length={chunk.length})"
        )
        if file_id:
            message = message + f" for file ID {file_id}"

        message = message + f": {error_messages.get(error_message, 'Unknown error')}."
        logger.error(message)
        raise exception

    return await retry(get_object_coro)


async def decrypt_object(file_id, encrypted_object, encryption_key, chunk):
    """
    Decrypt Encrypted Object.

    :param bytes encrypted_object: Encrypted object.
    :param bytes encryption_key: Encryption key.
    :param cterasdk.direct.types.Chunk chunk: Chunk.
    :returns: Decrypted Object.
    :rtype: bytes
    """
    try:
        return decrypt_block(encrypted_object, encryption_key)
    except DirectIOError:
        logger.error('Failed to decrypt block.')
        raise DecryptBlockError(file_id, chunk)


async def decompress_object(file_id, compressed_object, chunk):
    """
    Decompress Object.

    :param bytes compressed_object: Compressed object.
    :param cterasdk.direct.types.Chunk chunk: Chunk.
    :returns: Decompressed Object.
    :rtype: bytes
    """
    try:
        decompressed_object = decompress(compressed_object)
        if chunk.length != len(decompressed_object):
            logger.error('Expected block length does not match decrypted and decompressed block length.')
            raise BlockValidationException(file_id, chunk)
        return decompressed_object
    except DirectIOError:
        logger.error('Failed to decompress block.')
        raise DecompressBlockError(file_id, chunk)


async def process_chunk(client, file_id, chunk, encryption_key, semaphore):
    """
    Process a Chunk.

    :param cterasdk.clients.clients.AsyncClient client: Asynchronous HTTP Client.
    :param int file_id: File ID.
    :param cterasdk.direct.types.Chunk chunk: Chunk.
    :param str encryption_key: Encryption key.
    :param asyncio.Semaphore semaphore: Semaphore.

    :returns: Block
    :rtype: cterasdk.direct.types.Block
    """
    async def process(client, chunk, encryption_key):
        message = (
            f"Processing block {chunk.index} "
            f"(offset={chunk.offset}, length={chunk.length})"
        )
        if file_id:
            message = message + f" for file ID {file_id}"
        logger.debug(message)
        encrypted_object = await get_object(client, file_id, chunk)
        decrypted_object = await decrypt_object(file_id, encrypted_object, encryption_key, chunk)
        decompressed_object = await decompress_object(file_id, decrypted_object, chunk)
        return Block(file_id, chunk.index, chunk.offset, decompressed_object, chunk.length)

    if semaphore is not None:
        async with semaphore:
            return await process(client, chunk, encryption_key)
    return await process(client, chunk, encryption_key)


async def process_chunks(client, file_id, chunks, encryption_key, semaphore=None):
    """
    Process Chunks Asynchronously.

    :param cterasdk.clients.clients.AsyncClient client: Asynchronous HTTP Client.
    :param int file_id: File ID.
    :param list[cterasdk.direct.types.Chunk] chunks: Chunk.
    :param str encryption_key: Encryption key.
    :param asyncio.Semaphore,optional semaphore: Semaphore.
    :returns: List of futures.
    :rtype: list[asyncio.Task]
    """
    message = [f"Processing {len(chunks)} blocks"]
    if file_id:
        message.append(f"for file ID {file_id}")
    if semaphore:
        message.append(f"using up to {semaphore._value} workers")  # pylint: disable=protected-access
    logger.debug(' '.join(message))
    futures = []
    for chunk in chunks:
        futures.append(asyncio.create_task(process_chunk(client, file_id, chunk, encryption_key, semaphore)))
    return futures


def decrypt_encryption_key(file_id, wrapped_key, secret_access_key):
    """
    Decrypt Encryption Key.

    :param int file_id: File ID.
    :param str wrapped_key: Encryption Key.
    :param str secret_access_key: Secret Access Key.
    :returns: Decrypted Encryption Key.
    :rtype: bytes
    """
    try:
        return decrypt_key(wrapped_key, secret_access_key)
    except DirectIOError:
        logger.error('Failed to decrypt secret key.')
        raise DecryptKeyError(file_id)


def create_authorization_header(credentials):
    """
    Create Authorization Header.

    :param cterasdk.direct.credentials.BaseCredentials credentials: Credentials
    :returns: Authorization header as a dictionary.
    :rtype: dict
    """
    authorization_header = None

    if isinstance(credentials, Bearer):
        logger.debug('Initializing client using bearer token')
        authorization_header = f'Bearer {credentials.bearer}'

    elif isinstance(credentials, KeyPair):
        logger.debug('Initializing client using key pair.')
        authorization_header = f'Bearer {credentials.access_key_id}'

    return {'Authorization': authorization_header}


async def get_chunks(api, credentials, file_id):
    """
    Get Chunks.

    :param cterasdk.clients.clients.AsyncJSON api: Asynchronous JSON Client.
    :param int file_id: File ID.
    :returns: Wrapped key and file chunks.
    :rtype: cterasdk.direct.types.Metadata
    """
    async def get_chunks_coro():
        logger.debug('Listing blocks for file ID: %s', file_id)
        try:
            response = await api.get(f'{file_id}', headers=create_authorization_header(credentials))
            if not response.chunks:
                logger.error('Could not find blocks for file ID: %s.', file_id)
                raise BlocksNotFoundError(file_id)
            return Metadata(file_id, response)
        except HTTPError as error:
            if error.code == 400:
                raise NotFoundError(file_id)
            if error.code == 401:
                raise UnAuthorized(file_id)
            if error.code == 422:
                raise UnprocessableContent(file_id)
            raise error
        except ConnectionError:
            logger.error('Failed to list blocks for file ID: %s due to a connection error.', file_id)
            raise BlockListConnectionError(file_id)
        except asyncio.TimeoutError:
            logger.error('Timed out while listing blocks for file ID: %s.', file_id)
            raise BlockListTimeout(file_id)

    return await retry(get_chunks_coro)
