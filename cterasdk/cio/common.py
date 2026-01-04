import urllib.parse
from pathlib import PurePosixPath
from ..common import Object
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
    def relative(self):
        return self._reference.as_posix()

    @property
    def relative_encode(self):
        return urllib.parse.quote(self._reference.as_posix())

    @property
    def name(self):
        return self._reference.name

    @property
    def parent(self):
        return self.__class__(self._reference.parent.as_posix())  # pylint: disable=no-value-for-parameter

    @property
    def absolute(self):
        return f'/{self.scope.joinpath(self.reference).as_posix()}'

    @property
    def absolute_encode(self):
        return f'/{self.scope.joinpath(urllib.parse.quote(self.reference.as_posix())).as_posix()}'

    @property
    def absolute_parent(self):
        return self.parent.as_posix()

    @property
    def extension(self):
        return self.reference.suffix

    def join(self, p):
        """
        Join Path.

        :param str p: Path.
        """
        return self.__class__(self.reference.joinpath(p).as_posix())  # pylint: disable=no-value-for-parameter

    @property
    def parts(self):
        return self.reference.parts

    def __eq__(self, p):
        return self.absolute == p.absolute

    def __str__(self):
        return self.relative


class BaseResource(Object):
    """
    Class for a Filesystem Resource.

    :ivar str name: Resource name
    :ivar cterasdk.cio.common.BasePath path: Path Object
    :ivar bool is_dir: ``True`` if directory, ``False`` otherwise
    :ivar int size: Size
    :ivar datetime.datetime last_modified: Last Modified
    :ivar str extension: Extension
    """
    def __init__(self, name, path, is_dir, size, last_modified):
        super().__init__(name=name, path=path, is_dir=is_dir, size=size, last_modified=last_modified, extension=path.extension)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"'is_dir': {self.is_dir}, "
            f"'size': {self.size}, "
            f"'path': {self.path}}})"
        )

    def __str__(self):
        return str(self.path)


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
