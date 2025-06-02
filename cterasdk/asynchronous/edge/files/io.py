import logging
from ....cio.common import encode_request_parameter
from ....cio import edge as fs
from ....cio import exceptions
from ....exceptions import HTTPError


logger = logging.getLogger('cterasdk.edge')


async def listdir(edge, path):
    return fs.format_listdir_response(path.reference.as_posix(), await edge.io.propfind(path.absolute, 1))


async def walk(edge, path):
    paths = [fs.EdgePath.instance('/', path)]
    while len(paths) > 0:
        path = paths.pop(0)
        entries = await listdir(edge, path)
        for e in entries:
            if e.is_dir:
                paths.append(fs.EdgePath.instance('/', e))
            yield e


async def exists(edge, path):
    try:
        await edge.io.propfind(path.absolute, 0)
        return True
    except HTTPError:
        return False


async def mkdir(edge, path):
    with fs.makedir(path) as param:
        await edge.io.mkdir(param)
    return path.absolute


async def makedirs(edge, path):
    directories = path.parts
    for i in range(1, len(directories) + 1):
        path = fs.EdgePath(path.scope, '/'.join(directories[:i]))
        try:
            await mkdir(edge, path)
        except exceptions.RestrictedPathError:
            logger.warning('Creating a folder in the specified location is forbidden: %s', path.reference.as_posix())


async def copy(edge, path, destination=None, overwrite=False):
    with fs.copy(path, destination) as (src, dst):
        await edge.io.copy(src, dst, overwrite=overwrite)


async def move(edge, path, destination=None, overwrite=False):
    with fs.move(path, destination) as (src, dst):
        await edge.io.move(src, dst, overwrite=overwrite)


async def remove(edge, *paths):
    for path in fs.delete_generator(*paths):
        await edge.io.delete(path.absolute)


def handle(path):
    """
    Create function to retrieve file handle.

    :param cterasdk.cio.edge.EdgePath path: Path to file.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    async def wrapper(edge):
        """
        Get file handle.

        :param cterasdk.objects.synchronous.edge.Edge edge: Edge Filer object.
        """
        with fs.handle(path) as param:
            return await edge.io.download(param)
    return wrapper


def handle_many(directory, *objects):
    """
    Create function to retrieve zip archive

    :param cterasdk.cio.edge.EdgePath directory: Path to directory.
    :param args objects: List of files and folders.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    async def wrapper(edge):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.edge.Edge edge: Edge Filer object.
        :param str name: File name.
        :param object handle: File handle.
        """
        with fs.handle_many(directory, objects) as param:
            return await edge.io.download_zip('/admingui/api/status/fileManager/zip', encode_request_parameter(param))
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
    async def wrapper(edge):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.edge.Edge edge: Edge Filer object.
        """
        with fs.upload(name, destination, fd) as param:
            return await edge.io.upload('/actions/upload', param)
    return wrapper
