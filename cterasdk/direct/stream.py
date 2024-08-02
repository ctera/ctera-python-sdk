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
        self._offset = byte_range.start

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
                self._offset = fragment.offset + fragment.length
        except DirectIOAPIError as error:
            raise StreamError(error.filename, self._offset)
        except BlockError as error:
            raise StreamError(error.block.file_id, self._offset)
        finally:
            self.stop()
