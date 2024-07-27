from collections import namedtuple
from ...direct import client


Credentials = namedtuple('Credentials', ('access_key_id', 'secret_access_key'))
Credentials.__doc__ = 'Tuple holding the access and secret keys to access objects using DirectIO'
Credentials.access_key_id.__doc__ = 'Access key'
Credentials.secret_access_key.__doc__ = 'Secret Key'


class DirectIO:

    def __init__(self, baseurl, access_key_id=None, secret_access_key=None):
        """
        Initialize a DirectIO Client.

        :param str baseurl: Portal URL
        :param str,optional access_key_id: Access key
        :param str,optional secret_access_key: Secret key
        """
        self._client = client.DirectIO(baseurl, Credentials(access_key_id, secret_access_key))

    async def blocks(self, file_id, blocks=None):
        """
        Get Blocks.

        :param int file_id: File ID
        :param list[int],optional blocks: List of blocks to retrieve, defaults to all blocks.
        :returns: Blocks
        :rtype: list[cterasdk.direct.types.Block] or list[cterasdk.direct.types.BlockError]
        """
        return await self._client.blocks(file_id, blocks)

    async def streamer(self, file_id, byte_range=None):
        """
        Iterates over data chunks.

        :param int file_id: File ID.
        :returns: Stream Object
        :rtype: cterasdk.direct.stream.Streamer
        """
        return await self._client.streamer(file_id, byte_range)

    async def shutdown(self):
        await self._client.shutdown()
