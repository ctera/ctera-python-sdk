import logging
from ...cio.common import encode_request_parameter
from ...cio import edge as fs
from ...cio import exceptions


logger = logging.getLogger('cterasdk.edge')


def listdir(edge, path):
    with fs.listdir(path) as param:
        return edge.api.execute('/status/fileManager', 'listPhysicalFolders', param)


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
        except exceptions.RestrictedPathError:
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
        with fs.upload(name, destination, fd) as param:
            return edge.io.upload('/actions/upload', param)
    return wrapper
