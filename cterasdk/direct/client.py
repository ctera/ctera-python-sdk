import logging
import asyncio

from .types import Chunk, FilePart
from .crypto import decrypt_key, decrypt_block
from .decompressor import decompress

from ..objects.endpoints import DefaultBuilder, EndpointBuilder
from ..clients.asynchronous.clients import AsyncClient, AsyncJSON
from ..exceptions import UnAuthorized, BlocksNotFoundError, UnprocessableContent, ClientResponseException, \
    DecryptBlockError, DecryptKeyError, DecompressError


async def get_object(client, location):
    """
    Get Object from a Signed URL.

    :param str location: Signed URL.
    :returns: Object
    :rtype: bytes
    """
    logging.getLogger('cterasdk.direct').debug('Downloading Block.')
    response = await client.get(location)
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


async def process_chunk(client, chunk, encryption_key):
    """
    Process a Chunk.

    :param cterasdk.clients.asynchronous.clients.AsyncClient client: Asynchronous HTTP Client.
    :param cterasdk.direct.client.Chunk chunk: Chunk.
    :param str encryption_key: Encryption key.

    :returns: File Part
    :rtype: cterasdk.direct.client.FilePart
    """
    logging.getLogger('cterasdk.direct').debug('Processing Block. %s', {'number': chunk.index + 1})
    try:
        encrypted_object = await get_object(client, chunk.location)
        decrypted_object = await decrypt_object(encrypted_object, encryption_key)
        decompressed_object = await decompress_object(decrypted_object, chunk.length)
        return FilePart(chunk.index + 1, chunk.offset, decompressed_object, chunk.length)
    except ConnectionError as error:
        logging.getLogger('cterasdk.direct').error(f'Failed to retrieve block. Connection error: {error}')
        raise
    except DecryptBlockError:
        logging.getLogger('cterasdk.direct').error('Failed to decrypt block. %s', {'number': chunk.index + 1})
        raise
    except DecompressError:
        logging.getLogger('cterasdk.direct').error('Failed to decompress block. %s', {'number': chunk.index + 1})
        raise


async def process_chunks(client, chunks, encryption_key):
    """
    Process Chunks Asynchronously.

    :param cterasdk.clients.asynchronous.clients.AsyncClient client: Asynchronous HTTP Client.
    :param list[cterasdk.direct.client.Chunk] chunks: Chunk.
    :param str encryption_key: Encryption key.
    :returns: List of futures.
    :rtype: list[asyncio.Task]
    """
    logging.getLogger('cterasdk.direct').debug('Processing Blocks. %s', {'count': len(chunks)})
    futures = []
    for chunk in chunks:
        futures.append(asyncio.create_task(process_chunk(client, chunk, encryption_key)))
    return futures


def create_chunks(server_object):
    """
    Create Chunks.

    :param cterasdk.common.object.Object server_object: Server response.
    :returns: Chunk objects
    :rtype: list[cterasdk.direct.client.Chunk]
    """
    offset = 0
    chunks = []
    for index, chunk in enumerate(server_object):
        chunks.append(Chunk(index, offset, chunk.url, chunk.len))
        offset = offset + chunk.len
    return chunks


async def process_response(client, response, secret_access_key):
    """
    Process Response.

    :param cterasdk.clients.asynchronous.clients.AsyncClient client: Asynchronous HTTP Client.
    :param cterasdk.clients.asynchronous.clients.AsyncResponse response: Response.
    :param str secret_access_key: Secret Key.
    """
    try:
        encryption_key = decrypt_key(response.wrapped_key, secret_access_key)
        chunks = create_chunks(response.chunks)
        return await process_chunks(client, chunks, encryption_key)
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
    :rtype: cterasdk.common.object.Object
    """
    logging.getLogger('cterasdk.direct').debug('Listing blocks. %s', {'file_id': file_id})
    try:
        response = await api.get(f'{file_id}', headers=create_authorization_header(credentials))
        if not response.chunks:
            logging.getLogger('cterasdk.direct').debug('No blocks found. %s', {'file_id': file_id})
            raise BlocksNotFoundError(file_id)
        return response
    except ClientResponseException as error:
        if error.response.status == 401:
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

    async def parts(self, file_id, credentials):
        """
        Get File Parts.

        :param int file_id: File ID.
        :param cterasdk.objects.asynchronous.directio.Credentials,optional credentials: Credentials
        """
        credentials = credentials if credentials else self._credentials
        response = await get_chunks(self._api, credentials, file_id)
        return await process_response(self._client, response, credentials.secret_access_key)

    async def shutdown(self):
        await self._api.shutdown()
        await self._client.shutdown()
