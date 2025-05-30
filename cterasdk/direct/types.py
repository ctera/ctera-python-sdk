import copy
import base64
from ..common import Object, utils


class ByteRange:

    def __init__(self, start=None, end=None):
        """
        Initialize a Byte Range.

        :param int,optional start: Start byte, defaults to 0
        :param int,optional end: End byte, defaults to EOF
        """
        self._eof = True
        self._start = start if start is not None and start > -1 else 0
        if end is not None:
            if end < self._start:
                raise ValueError(f'Byte range end {end} must be greater than or equal to range start {start}.')
            self._eof = False
            self._end = end

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def eof(self):
        return self._eof

    @eof.setter
    def eof(self, eof):
        self._eof = eof

    @staticmethod
    def default():
        return ByteRange(0)


class CompressionLib:
    """
    Compression Library

    :ivar str Snappy: Snappy
    :ivar int Gzip: Gzip
    :ivar int Off: No Compression
    """
    Snappy = 'SNAPPY'
    Gzip = 'GZIP'
    Off = 'NONE'


class Chunk(Object):

    def __init__(self, index, offset, url, length):
        """
        Initialize a Chunk.

        :param int index: Chunk index.
        :param int offset: Chunk offset.
        :param str url: Signed URL.
        :param int length: Object length.
        """
        super().__init__(
            index=index,
            offset=offset,
            url=url,
            length=length
        )


class Metadata(Object):
    """
    CTERA Direct IO File Metadata
    """

    def __init__(self, file_id, server_object):
        """
        Initialize a Direct IO metadata response object.

        :param int file_id: File ID.
        :param cterasdk.common.object.Object server_object: Response Object.
        """
        super().__init__(
            file_id=file_id,
            encrypted=server_object.encrypt_info.data_encrypted,
            compressed=server_object.compression_type != CompressionLib.Off,
            chunks=Metadata._format_chunks(server_object.chunks)
        )
        self.encryption_key = server_object.encrypt_info.wrapped_key if self.encrypted else None
        self.compression_library = server_object.compression_type if self.compressed else None
        last_chunk = self.chunks[-1]
        self.size = last_chunk.offset + last_chunk.length

    @staticmethod
    def _format_chunks(server_object):
        """
        Create Chunks.

        :param int file_id: File ID.
        :param cterasdk.common.object.Object server_object: Server response.
        :param list[int] blocks: List of block numbers to retrieve.
        :returns: Chunk objects
        :rtype: list[cterasdk.direct.types.Chunk]
        """
        offset = 0
        chunks = []
        for index, chunk in enumerate(server_object, 1):
            chunks.append(Chunk(index, offset, chunk.url, chunk.len))
            offset = offset + chunk.len
        return chunks

    def serialize(self):
        """
        Serialize Direct IO metadata to a dictionary.
        """
        x = copy.deepcopy(self)
        if self.encrypted:
            x.encryption_key = utils.utf8_decode(base64.b64encode(self.encryption_key))
        return x


class Block:
    """Block"""

    def __init__(self, file_id, number, offset, data, length):
        """
        Initialize a Block.

        :param int file_id: File ID.
        :param int number: Block number.
        :param int offset: Block offset.
        :param bytes data: Bytes
        :param int length: Block length.
        """
        self._file_id = file_id
        self._number = number
        self._offset = offset
        self._data = data
        self._length = length

    @property
    def file_id(self):
        return self._file_id

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

    def fragment(self, byte_range):
        if byte_range.start > self._offset and byte_range.start < self._offset + self._length:
            start = byte_range.start - self._offset
        else:
            start = None

        if not byte_range.eof and byte_range.end < self._offset + self._length:
            end = byte_range.end - self._offset + 1
        else:
            end = None

        data = self._data[start:end]
        return Block(self._file_id, self._number, self._offset + start if start else self._offset, data, len(data))
