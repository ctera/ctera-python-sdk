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


class DirectIOResponse:

    def __init__(self, server_object):
        """
        Initialize a Get Response Object.

        :param int file_id: File ID.
        :param cterasdk.common.object.Object server_object: Response Object.
        """
        self._wrapped_key = server_object.wrapped_key
        self._chunks = DirectIOResponse._create_chunks(server_object.chunks)

    @staticmethod
    def _create_chunks(server_object):
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

    @property
    def wrapped_key(self):
        return self._wrapped_key

    @property
    def chunks(self):
        return self._chunks


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


class File:

    def __init__(self, file_id, encryption_key, chunks):
        """
        Initialize a File Object.

        :param int file_id: File ID.
        :param str encryption_key: Encryption Key.
        :param cterasdk.direct.types.Chunk chunks: List of Chunks.
        """
        self._file_id = file_id
        self._encryption_key = encryption_key
        self._chunks = chunks

    @property
    def file_id(self):
        return self._file_id

    @property
    def encryption_key(self):
        return self._encryption_key

    @property
    def chunks(self):
        return self._chunks

    @property
    def size(self):
        last_chunk = self._chunks[-1]
        return last_chunk.offset + last_chunk.length


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


class ChunkMetadata(Object):
    """
    Direct IO File Chunk Metadata Object

    :ivar str url: Part URL
    :ivar int index: Part Index
    :ivar int offset: Part Offset
    :ivar int length: Part Length
    """
    def __init__(self, url, index, offset, length):
        self.url = url
        self.index = index
        self.offset = offset
        self.length = length


class FileMetadata(Object):
    """
    Direct IO File Metadata Object
    """

    def __init__(self, f):
        self.encryption_key = utils.utf8_decode(base64.b64encode(f.encryption_key))
        self.chunks = [ChunkMetadata(chunk.location, chunk.index, chunk.offset, chunk.length) for chunk in f.chunks]
