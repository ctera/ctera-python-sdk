import asyncio
import cterasdk.settings

from . import filters
from .credentials import KeyPair, Bearer
from .lib import get_chunks, decrypt_encryption_key, process_chunks
from .types import ByteRange
from .stream import Streamer

from ..objects.endpoints import DefaultBuilder, EndpointBuilder
from ..clients.clients import AsyncClient, AsyncJSON


class DirectIO:

    async def __aenter__(self):
        return self

    def __init__(self, baseurl=None, access_key_id=None, secret_access_key=None, bearer=None):
        """
        Initialize a CTERA Direct IO Client.

        :param str baseurl: Portal URL
        :param str,optional access_key_id: Access key
        :param str,optional secret_access_key: Secret key
        :param str,optional bearer: Bearer token
        """
        self._api = AsyncJSON(EndpointBuilder.new(baseurl, '/directio'), settings=cterasdk.settings.io.direct.api.settings,
                              authenticator=lambda *_: True)
        self._client = AsyncClient(DefaultBuilder(), settings=cterasdk.settings.io.direct.storage.settings, authenticator=lambda *_: True)
        self._credentials = Bearer(bearer) if bearer else KeyPair(access_key_id, secret_access_key)

    async def _chunks(self, file_id):
        metadata = await get_chunks(self._api, self._credentials.bearer, file_id)
        if metadata.encrypted:
            metadata.encryption_key = decrypt_encryption_key(
                metadata.file_id,
                metadata.encryption_key,
                self._credentials.secret_access_key
            )
        return metadata

    async def metadata(self, file_id):
        """
        Get File Metadata.

        :param int file_id: File ID.
        """
        meta = await self._chunks(file_id)
        return meta.serialize()

    async def blocks(self, file_id, byte_range=None, max_workers=None):
        """
        Blocks API.

        :param int file_id: File ID.
        :param cterasdk.direct.types.ByteRange,optional byte_range: Byte Range.
        :param int,optional max_workers: Max concurrent tasks
        :returns: List of Blocks.
        :rtype: list[cterasdk.direct.types.Block]
        """
        meta = await self._chunks(file_id)
        byte_range = byte_range if byte_range is not None else ByteRange.default()
        executor = self.executor(filters.span(meta, byte_range), meta.encryption_key, meta.file_id, max_workers)
        return await executor()

    async def streamer(self, file_id, byte_range=None, max_workers=None):
        """
        Stream API.

        :param int file_id: File ID.
        :param cterasdk.direct.types.ByteRange,optional byte_range: Byte Range.
        :param int,optional max_workers: Max concurrent tasks
        :returns: Streamer Object
        :rtype: cterasdk.direct.stream.Streamer
        """
        meta = await self._chunks(file_id)
        byte_range = byte_range if byte_range is not None else ByteRange.default()
        max_workers = max_workers if max_workers else cterasdk.settings.io.direct.streamer.max_workers
        executor = self.executor(filters.span(meta, byte_range), meta.encryption_key, file_id, max_workers)
        return Streamer(executor, byte_range)

    def executor(self, chunks, encryption_key, file_id=None, max_workers=None):
        """
        Download Executor.

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

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
