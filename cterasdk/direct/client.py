import asyncio
from collections import namedtuple

import cterasdk.settings

from . import filters
from .lib import get_chunks, decrypt_encryption_key, process_chunks
from .types import File, ByteRange, FileMetadata
from .stream import Streamer

from ..objects.endpoints import DefaultBuilder, EndpointBuilder
from ..clients.settings import ClientSettings, ClientTimeout, TCPConnector
from ..clients.asynchronous.clients import AsyncClient, AsyncJSON


Credentials = namedtuple('Credentials', ('access_key_id', 'secret_access_key'))
Credentials.__doc__ = 'Tuple holding the access and secret keys to access objects using DirectIO'
Credentials.access_key_id.__doc__ = 'Access key'
Credentials.secret_access_key.__doc__ = 'Secret Key'


def client_settings(parameters):
    return ClientSettings(
        TCPConnector(parameters.ssl),
        ClientTimeout(**parameters.timeout.kwargs)
    )


class Client:

    def __init__(self, baseurl, credentials):
        """
        :param str baseurl: Portal URL
        :param cterasdk.objects.asynchronous.directio.Credentials credentials: Credentials
        """
        ctera_direct = cterasdk.settings.sessions.ctera_direct
        self._api = AsyncJSON(EndpointBuilder.new(baseurl, '/directio'), authenticator=lambda *_: True,
                              client_settings=client_settings(ctera_direct.api))
        self._client = AsyncClient(DefaultBuilder(), authenticator=lambda *_: True, client_settings=client_settings(ctera_direct.storage))
        self._credentials = credentials

    async def _direct(self, file_id):
        server_object = await get_chunks(self._api, self._credentials, file_id)
        encryption_key = decrypt_encryption_key(file_id, server_object.wrapped_key, self._credentials.secret_access_key)
        return File(file_id, encryption_key, server_object.chunks)

    async def metadata(self, file_id):
        """
        Direct IO Metadata API.

        :param int file_id: File ID.
        """
        return FileMetadata(await self._direct(file_id))

    async def blocks(self, file_id, blocks, max_workers):
        """
        Blocks API.

        :param int file_id: File ID.
        :param list[cterasdk.direct.exceptions.BlockInfo] blocks: List of BlockInfo objects,
         or list of integers identifying the block position.
        :param int max_workers: Max concurrent tasks. A task will be dispatched for each block if no limited was specified.
        :returns: List of Blocks.
        :rtype: list[cterasdk.direct.types.Block]
        """
        file = await self._direct(file_id)
        executor = await self.executor(filters.blocks(file, blocks), file.encryption_key, file_id, max_workers)
        return await executor()

    async def streamer(self, file_id, byte_range):
        """
        Stream API.

        :param int file_id: File ID.
        :param cterasdk.direct.types.ByteRange byte_range: Byte Range.
        :returns: Streamer Object
        :rtype: cterasdk.direct.stream.Streamer
        """
        file = await self._direct(file_id)
        byte_range = byte_range if byte_range is not None else ByteRange.default()
        max_workers = cterasdk.settings.sessions.ctera_direct.streamer.max_workers
        executor = await self.executor(filters.span(file, byte_range), file.encryption_key, file_id, max_workers)
        return Streamer(executor, byte_range)

    async def executor(self, chunks, encryption_key, file_id=None, max_workers=None):
        """
        Get Blocks.

        :param list[cterasdk.direct.types.Chunk] chunks: List of Chunks.
        :param str encryption_key: Decryption Key.
        :param int,optional file_id: File ID.
        :param int,optional max_workers: Max concurrent tasks.

        :returns: Callable Downloader
        :rtype: function
        """

        async def execute():
            """
            Asynchronous Executable of Chunk Retrieval Tasks.
            """
            return await process_chunks(self._client, file_id, chunks, encryption_key,
                                        asyncio.Semaphore(max_workers) if max_workers else None)

        return execute

    async def close(self):
        await self._api.close()
        await self._client.close()


class DirectIO:

    async def __aenter__(self):
        return self

    def __init__(self, baseurl=None, access_key_id=None, secret_access_key=None):
        """
        Initialize a DirectIO Client.

        :param str baseurl: Portal URL
        :param str,optional access_key_id: Access key
        :param str,optional secret_access_key: Secret key
        """
        self._client = Client(baseurl, Credentials(access_key_id, secret_access_key))

    async def metadata(self, file_id):
        """
        Get Metadata.

        :param int file_id: File ID
        """
        return await self._client.metadata(file_id)

    async def blocks(self, file_id, blocks=None, max_workers=None):
        """
        Get Blocks.

        :param int file_id: File ID
        :param list[cterasdk.direct.exceptions.BlockInfo] blocks: List of BlockInfo objects,
         or list of integers identifying the block position.
        :param int max_workers: Max concurrent tasks. A task will be dispatched for each block if no limited was specified.
        :returns: Blocks
        :rtype: list[cterasdk.direct.types.Block]
        """
        return await self._client.blocks(file_id, blocks, max_workers)

    async def streamer(self, file_id, byte_range=None):
        """
        Iterates over data chunks.

        :param int file_id: File ID.
        :param cterasdk.direct.types.ByteRange,optional byte_range: Byte Range.
        :returns: Stream Object
        :rtype: cterasdk.direct.stream.Streamer
        """
        return await self._client.streamer(file_id, byte_range)

    async def close(self):
        await self._client.close()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
