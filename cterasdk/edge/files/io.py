import logging
from ...cio.common import encode_request_parameter
from ...cio import edge as fs
from ...exceptions.transport import NotFound
from ...exceptions.io import RestrictedPathError, ResourceNotFoundError, NotADirectory


logger = logging.getLogger('cterasdk.edge')


def listdir(edge, path):
    return fs.format_listdir_response(path.reference.as_posix(), edge.io.propfind(path.absolute, 1))


def walk(edge, path):
    paths = [fs.EdgePath.instance('/', path)]
    while len(paths) > 0:
        path = paths.pop(0)
        entries = listdir(edge, path)
        for e in entries:
            if e.is_dir:
                paths.append(fs.EdgePath.instance('/', e))
            yield e


def exists(edge, path):
    present, *_ = metadata(edge, path, suppress_error=True)
    return present


def metadata(edge, path, suppress_error=False):
    """
    Get item metadata.

    :returns: A tuple indicating if a file exists, and its metadata
    """
    try:
        return True, fs.format_listdir_response(None, edge.io.propfind(path.absolute, 0))[0]
    except NotFound as error:
        if not suppress_error:
            raise ResourceNotFoundError(path.absolute) from error
        return False, None


def ensure_directory(edge, directory, suppress_error=False):
    present, resource = metadata(edge, directory, suppress_error=True)
    if (not present or not resource.is_dir) and not suppress_error:
        raise NotADirectory(directory.absolute)
    return resource.is_dir if present else False, resource


def mkdir(edge, path):
    with fs.makedir(path) as param:
        edge.io.mkdir(param)
    return path.absolute


def makedirs(edge, path):
    directories = path.parts
    for i in range(1, len(directories) + 1):
        path = fs.EdgePath(path.scope, '/'.join(directories[:i]))
        try:
            mkdir(edge, path)
        except RestrictedPathError:
            logger.warning('Creating a folder in the specified location is forbidden: %s', path.reference.as_posix())


def copy(edge, path, destination=None, overwrite=False):
    with fs.copy(path, destination) as (src, dst):
        edge.io.copy(src, dst, overwrite=overwrite)


def move(edge, path, destination=None, overwrite=False):
    with fs.move(path, destination) as (src, dst):
        edge.io.move(src, dst, overwrite=overwrite)


def remove(edge, *paths):
    for path in fs.delete_generator(*paths):
        edge.io.delete(path.absolute)


def handle(path):
    """
    Create function to retrieve file handle.

    :param cterasdk.cio.edge.EdgePath path: Path to file.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    def wrapper(edge):
        """
        Get file handle.

        :param cterasdk.objects.synchronous.edge.Edge edge: Edge Filer object.
        """
        with fs.handle(path) as param:
            return edge.io.download(param)
    return wrapper


def handle_many(directory, *objects):
    """
    Create function to retrieve zip archive

    :param cterasdk.cio.edge.EdgePath directory: Path to directory.
    :param args objects: List of files and folders.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    def wrapper(edge):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.edge.Edge edge: Edge Filer object.
        :param str name: File name.
        :param object handle: File handle.
        """
        with fs.handle_many(directory, objects) as param:
            return edge.io.download_zip('/admingui/api/status/fileManager/zip', encode_request_parameter(param))
    return wrapper


def _validate_destination(edge, name, destination):
    is_dir, *_ = ensure_directory(edge, destination, suppress_error=True)
    if not is_dir:
        is_dir, *_ = ensure_directory(edge, destination.parent)
        return destination.name, destination.parent
    return name, destination


def upload(name, destination, fd):
    """
    Create upload function

    :param str name: File name.
    :param cterasdk.cio.edge.EdgePath destination: Path to directory.
    :param object fd: File handle.
    :returns: Callable function to start the upload.
    :rtype: callable
    """
    def wrapper(edge):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.edge.Edge edge: Edge Filer object.
        """
        filename, directory = _validate_destination(edge, name, destination)
        with fs.upload(filename, directory, fd) as param:
            return edge.io.upload('/actions/upload', param)
    return wrapper
