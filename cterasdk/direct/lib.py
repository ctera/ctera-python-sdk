import logging
import asyncio

from .types import DirectIOResponse, Block
from .crypto import decrypt_key, decrypt_block
from .decompressor import decompress
from .exceptions import UnAuthorized, UnprocessableContent, BlocksNotFoundError, DownloadError, DownloadTimeout, BlockListTimeout, \
    DownloadConnectionError, DecryptKeyError, DecryptBlockError, NotFoundError, DecompressBlockError, BlockValidationException, \
    BlockListConnectionError, DirectIOError

from ..exceptions import ClientResponseException


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
            logging.getLogger('cterasdk.direct').debug('Failed attempt number %s. Retrying in %s seconds.', attempts, wait)
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
        parameters = {'file_id': file_id, 'number': chunk.index, 'offset': chunk.offset}
        logging.getLogger('cterasdk.direct').debug('Downloading Block. %s', parameters)
        try:
            response = await client.get(chunk.location)
            return await response.read()
        except ConnectionError:
            logging.getLogger('cterasdk.direct').error('Failed to download block. Connection error. %s', parameters)
            raise DownloadConnectionError(chunk)
        except asyncio.TimeoutError:
            logging.getLogger('cterasdk.direct').error('Failed to download block. Timed out. %s', parameters)
            raise DownloadTimeout(chunk)
        except ClientResponseException as error:
            logging.getLogger('cterasdk.direct').error('Failed to download block. Error. %s', parameters)
            raise DownloadError(error.response, chunk)

    return await retry(get_object_coro)


async def decrypt_object(encrypted_object, encryption_key, chunk):
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
        logging.getLogger('cterasdk.direct').error('Failed to decrypt block.')
        raise DecryptBlockError(chunk)


async def decompress_object(compressed_object, chunk):
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
            logging.getLogger('cterasdk.direct').error('Expected block length does not match decrypted and decompressed block length.')
            raise BlockValidationException(chunk)
        return decompressed_object
    except DirectIOError:
        logging.getLogger('cterasdk.direct').error('Failed to decompress block.')
        raise DecompressBlockError(chunk)


async def process_chunk(client, file_id, chunk, encryption_key, semaphore):
    """
    Process a Chunk.

    :param cterasdk.clients.asynchronous.clients.AsyncClient client: Asynchronous HTTP Client.
    :param int file_id: File ID.
    :param cterasdk.direct.types.Chunk chunk: Chunk.
    :param str encryption_key: Encryption key.
    :param asyncio.Semaphore semaphore: Semaphore.

    :returns: Block
    :rtype: cterasdk.direct.types.Block
    """
    async def process(client, chunk, encryption_key):
        parameters = {'file_id': file_id, 'number': chunk.index, 'offset': chunk.offset}
        logging.getLogger('cterasdk.direct').debug('Processing Block. %s', parameters)

        encrypted_object = await get_object(client, file_id, chunk)
        decrypted_object = await decrypt_object(encrypted_object, encryption_key, chunk)
        decompressed_object = await decompress_object(decrypted_object, chunk)
        return Block(file_id, chunk.index, chunk.offset, decompressed_object, chunk.length)

    if semaphore is not None:
        async with semaphore:
            return await process(client, chunk, encryption_key)
    return await process(client, chunk, encryption_key)


async def process_chunks(client, file_id, chunks, encryption_key, semaphore=None):
    """
    Process Chunks Asynchronously.

    :param cterasdk.clients.asynchronous.clients.AsyncClient client: Asynchronous HTTP Client.
    :param int file_id: File ID.
    :param list[cterasdk.direct.types.Chunk] chunks: Chunk.
    :param str encryption_key: Encryption key.
    :param asyncio.Semaphore,optional semaphore: Semaphore.
    :returns: List of futures.
    :rtype: list[asyncio.Task]
    """
    parameters = {'file_id': file_id, 'blocks': len(chunks)}
    if semaphore:
        parameters['max_workers'] = semaphore._value  # pylint: disable=protected-access
    logging.getLogger('cterasdk.direct').debug('Processing Blocks. %s', parameters)
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
        logging.getLogger('cterasdk.direct').error('Failed to decrypt secret key.')
        raise DecryptKeyError(file_id)


def create_authorization_header(credentials):
    """
    Create Authorization Header.

    :param cterasdk.objects.asynchronous.direct.Credentials credentials: Credentials
    :returns: Authorization header as a dictionary.
    :rtype: dict
    """
    return {
        'Authorization': f'Bearer {credentials.access_key_id}'
    }


async def get_chunks(api, credentials, file_id):
    """
    Get Chunks.

    :param cterasdk.clients.asynchronous.clients.AsyncJSON api: Asynchronous JSON Client.
    :param int file_id: File ID.
    :returns: Wrapped key and file chunks.
    :rtype: cterasdk.direct.types.DirectIOResponse
    """
    async def get_chunks_coro():
        parameters = {'file_id': file_id}
        logging.getLogger('cterasdk.direct').debug('Listing blocks. %s', parameters)
        try:
            response = await api.get(f'{file_id}', headers=create_authorization_header(credentials))
            if not response.chunks:
                logging.getLogger('cterasdk.direct').error('Blocks not found. %s', parameters)
                raise BlocksNotFoundError(file_id)
            return DirectIOResponse(response)
        except ClientResponseException as error:
            if error.response.status == 400:
                raise NotFoundError(file_id)
            if error.response.status == 401:
                raise UnAuthorized(file_id)
            if error.response.status == 422:
                raise UnprocessableContent(file_id)
            raise error
        except ConnectionError:
            logging.getLogger('cterasdk.direct').error('Failed to list blocks. Connection error. %s', parameters)
            raise BlockListConnectionError(file_id)
        except asyncio.TimeoutError:
            logging.getLogger('cterasdk.direct').error('Failed to list blocks. Timed out. %s', parameters)
            raise BlockListTimeout(file_id)

    return await retry(get_chunks_coro)
