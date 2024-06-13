import logging
import asyncio

from .crypto import decrypt_key, decrypt_block
from .decompressor import decompress

from ..objects.endpoints import DefaultBuilder, EndpointBuilder
from ..clients.asynchronous.clients import AsyncClient, AsyncJSON


async def get_object(client, location):
    """
    Get Object from a Signed URL.

    :param str location: Signed URL.
    :returns: Object
    :rtype: bytes
    """
    print(location)
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


class Chunk:
    """Chunk to Retrieve"""

    def __init__(self, index, offset, location, length):
        """
        Initialize a Chunk.

        :param int index: Chunk index.
        :param int offset: Chunk offset.
        :param str location: Signed URL.
        :param int length: Object length.
        """
        self._index = index
        self._offset = offset
        self._location = location
        self._length = length

    @property
    def index(self):
        return self._index
    
    @property
    def offset(self):
        return self._offset
    
    @property
    def location(self):
        return self._location
    
    @property
    def length(self):
        return self._length
    

class FilePart:
    """File Part"""

    def __init__(self, number, offset, data, length):
        """
        Initialize a File Part.

        :param int number: Part number.
        :param int offset: Part offset.
        :param bytes data: Bytes
        :param int length: Part length.
        """
        self._number = number
        self._offset = offset
        self._data = data
        self._length = length

    @property
    def number(self):
        return self._number
    
    @property
    def offset(self):
        return self._offset
    
    @property
    def data(self):
        return self._data
    
    @property
    def length(self):
        return self._length


async def process_chunk(client, chunk, encryption_key):
    """
    Process a Chunk.

    :param cterasdk.clients.asynchronous.clients.AsyncClient client: Asynchronous HTTP Client.
    :param cterasdk.direct.client.Chunk chunk: Chunk.
    :param str encryption_key: Encryption key.
    
    :returns: File Part
    :rtype: cterasdk.direct.client.FilePart
    """
    try:
        encrypted_object = await get_object(client, chunk.location)
        decrypted_object = await decrypt_object(encrypted_object, encryption_key)
        decompressed_object = await decompress_object(decrypted_object, chunk.length)
        return FilePart(chunk.index + 1, chunk.offset, decompressed_object, chunk.length)
    except ConnectionError as error:
        logging.getLogger('cterasdk.direct').error(f'Could not retrieve object. Connection error: {error}')
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
    encryption_key = decrypt_key(response.wrapped_key, secret_access_key)
    chunks = create_chunks(response.chunks)
    return await process_chunks(client, chunks, encryption_key)


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
    return await api.get(f'{file_id}', headers=create_authorization_header(credentials))


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
        self._api = AsyncJSON(EndpointBuilder.new(baseurl, '/directio'), authenticator=self._authenticator)
        self._client = AsyncClient(DefaultBuilder(), authenticator=self._authenticator)
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

    def _authenticator(self, url):
        return True
    
    async def shutdown(self):
        await self._api.shutdown()
        await self._client.shutdown()