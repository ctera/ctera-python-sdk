class Chunk:
    """Chunk to Retrieve"""

    def __init__(self, file_id, index, offset, location, length):
        """
        Initialize a Chunk.

        :param int index: File ID.
        :param int index: Chunk index.
        :param int offset: Chunk offset.
        :param str location: Signed URL.
        :param int length: Object length.
        """
        self._file_id = file_id
        self._index = index
        self._offset = offset
        self._location = location
        self._length = length

    @property
    def file_id(self):
        return self._file_id

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


class Block:
    """Block"""

    def __init__(self, number, offset, data, length):
        """
        Initialize a Block.

        :param int number: Block number.
        :param int offset: Block offset.
        :param bytes data: Bytes
        :param int length: Block length.
        """
        self._number = number
        self._offset = offset
        self._data = data
        self._length = length

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


class BlockError:
    """Block Error"""

    def __init__(self, file_id, number, error):
        self._file_id = file_id
        self._number = number
        self._error = error

    @property
    def file_id(self):
        return self._file_id

    @property
    def number(self):
        return self._number

    @property
    def error(self):
        return self._error

    @staticmethod
    def instance(file_id, number, error):
        """
        Initialize a Block Error Object.

        :param int file_id: File ID.
        :param int number: Block number.
        :param cterasdk.exceptions.DirectIOError error: Exception Object.
        """
        return BlockError(file_id, number, error)
