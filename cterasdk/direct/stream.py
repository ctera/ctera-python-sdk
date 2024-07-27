import logging
from ..exceptions import DecryptBlockError, DecompressError, BlockError, StreamError


class Streamer:
    """
    Direct IO Streamer.
    """

    def __init__(self, executor, byte_range):
        """
        Initialize a Streamer.

        :param callable _executor: Asynchronous Direct IO Callable.
        :param cterasdk.direct.types.ByteRange byte_range: Byte Range.
        """
        self._executor = executor
        self._downloads = None
        self._byte_range = byte_range

    async def stream(self):
        cursor = 0
        self._downloads = await self._executor()
        while cursor < len(self._downloads):
            block = await self._downloads[cursor]
            fragment = block.fragment(self._byte_range)
            logging.getLogger('cterasdk.direct').debug('Streamer Fragment. %s', {'offset': fragment.offset, 'length': fragment.length})
            yield fragment
            cursor = cursor + 1
