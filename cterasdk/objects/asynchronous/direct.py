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

    async def blocks(self, file_id, access_key_id=None, secret_access_key=None, *, blocks=None):
        """
        Get Blocks.

        :param int file_id: File ID
        :param str,optional access_key_id: Access key
        :param str,optional secret_access_key: Secret key
        :param list[int],optional blocks: List of blocks to retrieve, defaults to all blocks.
        :returns: Blocks
        :rtype: list[cterasdk.direct.types.Block] or list[cterasdk.direct.types.BlockError]
        """
        credentials = Credentials(access_key_id, secret_access_key) if all([access_key_id, secret_access_key]) else None
        return await self._client.blocks(file_id, credentials, blocks)

    async def iter_content(self, file_id, access_key_id=None, secret_access_key=None):
        """
        Iterates over data chunks.

        :param int file_id: File ID.
        :param str,optional access_key_id: Access key
        :param str,optional secret_access_key: Secret key
        """
        credentials = Credentials(access_key_id, secret_access_key) if all([access_key_id, secret_access_key]) else None
        return await self._client.iter_content(file_id, credentials)

    async def shutdown(self):
        await self._client.shutdown()
