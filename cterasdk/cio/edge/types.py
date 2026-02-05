import urllib.parse
from datetime import datetime
from ..common import BasePath, BaseResource


class EdgePath(BasePath):
    """
    Edge Filer Path Object
    """
    Namespace = '/'

    def __init__(self, reference):
        super().__init__(EdgePath.Namespace, reference or '.')


class EdgeResource(BaseResource):
    """
    Class for a Edge Filer Filesystem Resource.

    :ivar str name: Resource name
    :ivar cterasdk.cio.types.EdgePath path: Path Object
    :ivar bool is_dir: ``True`` if directory, ``False`` otherwise
    :ivar int size: Size
    :ivar datetime.datetime created_at: Last Modified
    :ivar datetime.datetime last_modified: Last Modified
    :ivar str extension: Extension
    """
    def __init__(self, path, is_dir, size, created_at, last_modified):
        super().__init__(path.name, path, is_dir, size, last_modified)
        self.created_at = created_at

    @staticmethod
    def decode_reference(href):
        namespace = '/localFiles'
        return urllib.parse.unquote(href[href.index(namespace)+len(namespace) + 1:])

    @staticmethod
    def from_server_object(server_object):
        return EdgeResource(
            EdgePath(EdgeResource.decode_reference(server_object.href)),
            server_object.getcontenttype == 'httpd/unix-directory',
            server_object.getcontentlength,
            datetime.fromisoformat(server_object.creationdate),
            datetime.strptime(server_object.getlastmodified, "%a, %d %b %Y %H:%M:%S GMT")
        )


class ResourceState:
    """
    Filesystem Resource Synchronization Status

    :ivar cterasdk.cio.types.EdgePath path: Path Object
    :ivar bool in_cache: ``True`` if the resource is cached ``False`` otherwise.
    """
    def __init__(self, path, in_cache):
        self.path = path
        self.in_cache = in_cache

    @staticmethod
    def from_server_object(server_object, parent):
        in_cache = None
        if server_object.syncStatus == 'Synced':
            in_cache = True
        elif server_object.syncStatus == 'Stub':
            in_cache = False
        if in_cache is not None:
            return ResourceState(parent.join(server_object.name), in_cache)
        raise ValueError(f'Could not determine synchronization status ({server_object.syncStatus}) for: {server_object.name}')

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"'in_cache': {self.in_cache}, "
            f"'path': {self.path})"
        )

    def __str__(self):
        return str(self.path)


def resolve(path):
    """
    Resolve Path

    :param object path: Path
    """
    if isinstance(path, EdgePath):
        return path

    if isinstance(path, EdgeResource):
        return path.path

    if path is None or isinstance(path, str):
        return EdgePath(path)

    raise ValueError(f'Error: Could not resolve path: {path}. Type: {type(path)}')


def create_generator(paths):
    """
    Create Path Object Generator Object.

    :param object paths: List or a tuple
    """
    def wrapper():
        for path in paths:
            if isinstance(path, tuple):
                yield resolve(path[0]), resolve(path[1])
            else:
                yield resolve(path)
    return wrapper()


def automatic_resolution(p):
    """
    Automatic Resolution of Path Object

    :param object p: Path
    """
    if isinstance(p, (list, tuple)):
        return create_generator(p)

    return resolve(p)
