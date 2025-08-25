from pathlib import PurePosixPath
from ..objects.uri import quote
from ..common.utils import utf8_decode
from ..convert.serializers import toxmlstr


class BasePath:
    """Base Path for CTERA Portal and CTERA Edge"""

    def __init__(self, scope, reference):
        """
        Initialize a Base Path.

        :param str scope: Scope.
        :param str reference: Reference.
        """
        if isinstance(scope, str):
            scope = scope.lstrip('/')
        if isinstance(reference, str):
            reference = reference.lstrip('/')
        self._scope = PurePosixPath(scope)
        self._reference = PurePosixPath(reference)

    @property
    def scope(self):
        return self._scope

    @property
    def reference(self):
        return self._reference

    @property
    def name(self):
        return self._reference.name

    @property
    def parent(self):
        return self.__class__(self._scope.as_posix(), self._reference.parent.as_posix())

    @property
    def absolute(self):
        return f'/{self.scope.joinpath(self.reference).as_posix()}'

    @property
    def absolute_encode(self):
        return f'/{self.scope.joinpath(quote(self.reference.as_posix())).as_posix()}'

    @property
    def absolute_parent(self):
        return self.parent.as_posix()

    def join(self, p):
        """
        Join Path.

        :param str p: Path.
        """
        return self.__class__(self._scope.as_posix(), self.reference.joinpath(p).as_posix())

    @property
    def parts(self):
        return self.reference.parts

    def __str__(self):
        return self.absolute


def encode_stream(fd, size):
    if isinstance(fd, str):
        fd = fd.encode('utf-8')
    if isinstance(fd, bytes):
        size = str(len(fd))
    return fd, size


def encode_request_parameter(param):
    return dict(
        inputXML=utf8_decode(toxmlstr(param))
    )
