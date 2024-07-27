import logging
import asyncio

from . import filters
from .types import DirectIOResponse, File, Block, ByteRange
from .crypto import decrypt_key, decrypt_block
from .decompressor import decompress
from .stream import Streamer

from ..objects.endpoints import DefaultBuilder, EndpointBuilder
from ..clients.asynchronous.clients import AsyncClient, AsyncJSON
from ..exceptions import UnAuthorized, BlocksNotFoundError, UnprocessableContent, ClientResponseException, \
    DecryptBlockError, DecryptKeyError, DecompressError, NotFoundError, BlockError


async def get_object(client, chunk):
    """
    Get Object from a Signed URL.

    :param cterasdk.direct.types.Chunk chunk: Chunk.
    :returns: Object
    :rtype: bytes
    """
    logging.getLogger('cterasdk.direct').debug('Downloading Block. %s', {'file_id': chunk.file_id, 'number': chunk.index})
    response = await client.get(chunk.location)
    return await response.read()


async def decrypt_object(encrypted_object, encryption_key):
    """
    Decrypt Encrypted Object.

    :param bytes encrypted_object: Encrypted object.
    :param bytes encryption_key: Encryption key.
    :returns: Decrypted Object.
    :rtype: bytes
    """
    return decrypt_block(encrypted_object, encryption_key)


async def decompress_object(compressed_object, expected_length):
    """
    Decompress Object.

    :param bytes compressed_object: Compressed object.
    :param int expected_length: Object length.
    :returns: Decompressed Object.
    :rtype: bytes
    """
    decompressed_object = decompress(compressed_object)
    assert expected_length == len(decompressed_object)
    return decompressed_object


async def process_chunk(client, chunk, encryption_key, semaphore):
    """
    Process a Chunk.

    :param cterasdk.clients.asynchronous.clients.AsyncClient client: Asynchronous HTTP Client.
    :param cterasdk.direct.types.Chunk chunk: Chunk.
    :param str encryption_key: Encryption key.
    :param asyncio.Semaphore semaphore: Semaphore.

    :returns: Block
    :rtype: cterasdk.direct.types.Block
    """
    async def process(client, chunk, encryption_key):
        logging.getLogger('cterasdk.direct').debug('Processing Block. %s', {'file_id': chunk.file_id, 'number': chunk.index})
        try:
            encrypted_object = await get_object(client, chunk)
            decrypted_object = await decrypt_object(encrypted_object, encryption_key)
            decompressed_object = await decompress_object(decrypted_object, chunk.length)
            return Block(chunk.index, chunk.offset, decompressed_object, chunk.length)
        except (ConnectionError, DecryptBlockError, DecompressError) as error:
            logging.getLogger('cterasdk.direct').error('Failed to process block.')
            raise BlockError(chunk.file_id, chunk.index, error)

    if semaphore is not None:
        async with semaphore:
            return await process(client, chunk, encryption_key)
    return await process(client, chunk, encryption_key)


async def process_chunks(client, chunks, encryption_key, semaphore=None):
    """
    Process Chunks Asynchronously.

    :param cterasdk.clients.asynchronous.clients.AsyncClient client: Asynchronous HTTP Client.
    :param list[cterasdk.direct.types.Chunk] chunks: Chunk.
    :param str encryption_key: Encryption key.
    :param asyncio.Semaphore,optional semaphore: Semaphore.
    :returns: List of futures.
    :rtype: list[asyncio.Task]
    """
    logging.getLogger('cterasdk.direct').debug('Processing Blocks. %s', {'file_id': chunks[0].file_id, 'count': len(chunks)})
    futures = []
    for chunk in chunks:
        futures.append(asyncio.create_task(process_chunk(client, chunk, encryption_key, semaphore)))
    return futures
    

def decrypt_encryption_key(wrapped_key, secret_access_key):
    try:
        return decrypt_key(wrapped_key, secret_access_key)
    except DecryptKeyError:
        logging.getLogger('cterasdk.direct').error('Failed to decrypt secret key.')
        raise


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
    message_attributes = {'file_id': file_id}
    logging.getLogger('cterasdk.direct').debug('Listing blocks. %s', message_attributes)
    try:
        response = await api.get(f'{file_id}', headers=create_authorization_header(credentials))
        if not response.chunks:
            logging.getLogger('cterasdk.direct').error('Blocks not found. %s', message_attributes)
            raise BlocksNotFoundError(file_id)
        return DirectIOResponse(file_id, response)
    except ClientResponseException as error:
        if error.response.status == 400:
            raise NotFoundError(file_id)
        elif error.response.status == 401:
            raise UnAuthorized()
        elif error.response.status == 422:
            raise UnprocessableContent(file_id)
        raise error


def validate_file_identifier(file_id):
    """
    Validate File ID.

    :param int file_id: File ID.
    :raises: ValueError
    """
    if not isinstance(file_id, int):
        ValueError('Invalid file identifier.')


class DirectIO:

    def __init__(self, baseurl, credentials):
        """
        :param str baseurl: Portal URL
        :param cterasdk.objects.asynchronous.directio.Credentials credentials: Credentials
        """
        self._api = AsyncJSON(EndpointBuilder.new(baseurl, '/directio'), authenticator=lambda *_: True)
        self._client = AsyncClient(DefaultBuilder(), authenticator=lambda *_: True)
        self._credentials = credentials

    async def _file(self, file_id):
        server_object = await get_chunks(self._api, self._credentials, file_id)
        encryption_key = decrypt_encryption_key(server_object.wrapped_key, self._credentials.secret_access_key)
        return File(file_id, encryption_key, server_object.chunks)

    async def blocks(self, file_id, blocks):
        """
        Blocks API.

        :param int file_id: File ID.
        :param list[cterasdk.direct.types.BlockError] blocks: List of ``BlockError`` objects or block numbers.
        """
        file = await self._file(file_id)
        executor = self._executor(filters.blocks(file, blocks), file.encryption_key)
        return await executor()

    async def streamer(self, file_id, byte_range):
        """
        Stream API.

        :param int file_id: File ID.
        :param cterasdk.direct.types.ByteRange,optional byte_range: Byte Range.
        :returns: Streamer Object
        :rtype: cterasdk.direct.stream.Streamer
        """
        byte_range = byte_range if byte_range else ByteRange.default()
        file = await self._file(file_id)
        executor = self._executor(filters.bytes(file, byte_range), file.encryption_key, asyncio.Semaphore(50))
        return Streamer(executor, byte_range)

    def _executor(self, chunks, encryption_key, semaphore=None):
        """
        Get Blocks.

        :param list[cterasdk.direct.types.Chunk] chunks: List of Chunks.
        :param str encryption_key: Decryption Key.
        :param asyncio.Semaphore: Sempahore.

        :returns: Callable Downloader
        :rtype: function
        """
        async def execute():
            """
            Asynchronous Executable of Chunk Retrieval Tasks.
            """
            return await process_chunks(self._client, chunks, encryption_key, semaphore)

        return execute

    async def shutdown(self):
        await self._api.shutdown()
        await self._client.shutdown()
