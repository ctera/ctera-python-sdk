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


class FilePart:
    """File Part"""

    def __init__(self, number, offset, data, length):
        """
        Initialize a File Part.
        :param int number: Part number.
        :param int offset: Part offset.
        :param bytes data: Bytes
        :param int length: Part length.
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
