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

    def __init__(self, offset, url, length):
        """
        Initialize a Chunk.

        :param int offset: Chunk offset.
        :param str url: Signed URL.
        :param int length: Object length.
        """
        super().__init__(
            offset=offset,
            url=url,
            length=length
        )


class MetadataPart(Object):
    """
    CTERA Direct I/O File Metadata Part

    :ivar int start: Starting offset.
    :ivar int end: Ending offset.
    :ivar int length: Length of the range in bytes.
    :ivar bool encrypted: Indicates whether the range data is encrypted.
    :ivar str encryption_key: Encryption key used for the range data.
    :ivar bool compressed: Indicates whether the range data is compressed.
    :ivar str compression_alg: Compression algorithm used for the range data.
    :ivar list[cterasdk.common.object.Object] chunks: List of Chunk Objects.
    """
    def __init__(self, offset, end, encrypted, encryption_key, compressed, compression_alg, chunks):
        """
        Initialize a Direct IO metadata response object.

        :param int offset: Starting offset.
        :param int end: Ending offset.
        :param bool encrypted: Indicates whether the file is encrypted.
        :param str encryption_key: Encryption key used for the file.
        :param bool compressed: Indicates whether the file is compressed.
        :param str compression_alg: Compression algorithm used for the file.
        :param list[cterasdk.common.object.Object] chunks: List of Chunk Objects.
        """
        super().__init__(
            start=offset,
            end=end,
            length=(end - offset) + 1,
            encrypted=encrypted,
            encryption_key=encryption_key,
            compressed=compressed,
            compression_alg=compression_alg
        )
        for chunk in chunks:
            self.chunks.append(Chunk(offset, chunk.url, chunk.len))
            offset = offset + chunk.len

    @staticmethod
    def from_server_object(server_object):
        compressed = server_object.compression_type != CompressionLib.Off
        start, end = map(int, server_object.actual_blocks_range.range.split('-'))
        return MetadataPart(
            start,
            end,
            server_object.encrypt_info.data_encrypted,
            server_object.encrypt_info.wrapped_key if server_object.encrypt_info.data_encrypted else None,
            compressed,
            server_object.compression_type if compressed else None
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"{{'start': {self.start}, "
            f"'end': {self.end}, "
            f"'encrypted': {self.encrypted}, "
            f"'compressed': {self.compressed}, "
            f"'length': {self.length}, "
            f"'chunks': {len(self.chunks)}}})"
        )


class Metadata(Object):
    """
    CTERA Direct I/O File Metadata

    :ivar int file_id: File ID.
    :ivar int file_size: File Size.
    :ivar list[cterasdk.direct.types.MetadataPart] parts: List of Metadata Parts.
    :ivar bool encrypted: Indicates whether the range data is encrypted.
    :ivar str encryption_key: Encryption key used for the range data.
    :ivar bool compressed: Indicates whether the range data is compressed.
    :ivar str compression_alg: Compression algorithm used for the range data.
    """
    def __init__(self, file_id, *parts):
        """
        Initialize a Direct IO metadata response object.

        :param int file_id: File ID.
        :param list[cterasdk.direct.types.MetadataPart] parts: List of Metadata Parts.
        """
        super().__init__(file_id=file_id, parts=parts)

    @property
    def size(self):
        return self.parts[0].actual_blocks_range.file_size

    @property
    def encrypted(self):
        return self.parts[0].encrypted

    @property
    def encryption_key(self):
        return self.parts[0].encryption_key

    @property
    def compressed(self):
        return self.parts[0].compressed

    @property
    def compression_alg(self):
        return self.parts[0].compression_alg

    @property
    def start(self):
        return self.parts[0].start

    @property
    def end(self):
        return self.parts[-1].end

    def serialize(self):
        """
        Serialize Direct I/O metadata to a dictionary.
        """
        chunks = []
        for part in self.parts:
            chunks.extend(part.chunks)

        return {
            'file_id': self.file_id,
            'size': self.size,
            'encrypted': self.encrypted,
            'encryption_key': utils.utf8_decode(base64.b64encode(self.encryption_key)) if self.encrypted else None,
            'compressed': self.compressed,
            'compression_alg': self.compression_alg,
            'chunks': chunks
        }

    def __repr__(self):
        return str(self)

    def __str__(self):
        d = self.serialize()
        d.pop('encryption_key')
        d['chunks'] = len(d['chunks'])
        return d


class Block:
    """Block"""

    def __init__(self, file_id, offset, data, length):
        """
        Initialize a Block.

        :param int file_id: File ID.
        :param int offset: Block offset.
        :param bytes data: Bytes
        :param int length: Block length.
        """
        self._file_id = file_id
        self._offset = offset
        self._data = data
        self._length = length

    @property
    def file_id(self):
        return self._file_id

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
