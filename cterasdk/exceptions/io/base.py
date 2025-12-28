EREMOTEIO = 121


class BaseIOError(IOError):
    """Base CTERA IO Error"""


class PathError(BaseIOError):
    """
    Object I/O Error

    :ivar str path: Path
    """
    def __init__(self, errno, strerror, filename, filename2=None):
        super().__init__(errno, strerror, filename, None, filename2)
        self.path = filename
