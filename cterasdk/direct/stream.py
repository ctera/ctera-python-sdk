import logging
from .exceptions import DirectIOAPIError, BlockError, StreamError


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

    def stop(self):
        """
        Stop Stream.
        """
        for download in self._downloads:
            download.cancel()

    async def start(self):
        """
        Stop Stream.
        """
        try:
            self._downloads = await self._executor()
            for download in self._downloads:
                block = await download
                fragment = block.fragment(self._byte_range)
                logging.getLogger('cterasdk.direct').debug('Streamer Fragment. %s', {'offset': fragment.offset, 'length': fragment.length})
                yield fragment
        except DirectIOAPIError as error:
            raise StreamError(error.filename)
        except BlockError as error:
            raise StreamError(error.block.file_id)
        finally:
            self.stop()
