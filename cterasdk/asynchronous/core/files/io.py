import logging
from ....cio.common import encode_request_parameter
from ....cio import core as fs
from ....exceptions.io import ResourceNotFoundError, NotADirectory, ResourceExistsError
from .. import query
from ....lib import FetchResourcesResponse


logger = logging.getLogger('cterasdk.core')


async def listdir(core, path, depth=None, include_deleted=False, search_criteria=None, limit=None):
    with fs.fetch_resources(path, depth, include_deleted, search_criteria, limit) as param:
        if param.depth > 0:
            return query.iterator(core, '', param, 'fetchResources', callback_response=FetchResourcesResponse)
        return await core.v1.api.execute('', 'fetchResources', param)


async def exists(core, path):
    present, *_ = await metadata(core, path, suppress_error=True)
    return present


async def metadata(core, path, suppress_error=False):
    """
    Get item metadata.

    :returns: A tuple indicating if a file exists, and its metadata
    """
    response = await listdir(core, path, 0)
    if response.root is None:
        if not suppress_error:
            raise ResourceNotFoundError(path.absolute)
        return False, None
    return True, response.root


async def versions(core, path):
    with fs.versions(path):
        return await core.v1.api.execute('', 'listSnapshots', path.absolute)


async def walk(core, scope, path, include_deleted=False):
    paths = [fs.CorePath.instance(scope, path)]
    while len(paths) > 0:
        path = paths.pop(0)
        entries = await listdir(core, path, include_deleted=include_deleted)
        async for e in entries:
            if e.isFolder:
                paths.append(fs.CorePath.instance(scope, e))
            yield e


async def mkdir(core, path):
    with fs.makedir(path) as param:
        response = await core.v1.api.execute('', 'makeCollection', param)
    fs.accept_response(response, path.reference.as_posix())


async def makedirs(core, path):
    directories = path.parts
    for i in range(1, len(directories) + 1):
        path = fs.CorePath.instance(path.scope, '/'.join(directories[:i]))
        try:
            await mkdir(core, path)
        except ResourceExistsError:
            logger.debug('Resource already exists: %s', path.reference.as_posix())


async def rename(core, path, name):
    with fs.rename(path, name) as param:
        return await core.v1.api.execute('', 'moveResources', param)


async def remove(core, *paths):
    with fs.delete(*paths) as param:
        return await core.v1.api.execute('', 'deleteResources', param)


async def recover(core, *paths):
    with fs.recover(*paths) as param:
        return await core.v1.api.execute('', 'restoreResources', param)


async def copy(core, *paths, destination=None):
    with fs.copy(*paths, destination=destination) as param:
        return await core.v1.api.execute('', 'copyResources', param)


async def move(core, *paths, destination=None):
    with fs.move(*paths, destination=destination) as param:
        return await core.v1.api.execute('', 'moveResources', param)


async def ensure_directory(core, directory, suppress_error=False):
    present, resource = await metadata(core, directory, suppress_error=True)
    if (not present or not resource.isFolder) and not suppress_error:
        raise NotADirectory(directory.absolute)
    return resource.isFolder if present else False, resource


def handle(path):
    """
    Create function to retrieve file handle.

    :param cterasdk.cio.edge.CorePath path: Path to file.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    async def wrapper(core):
        """
        Get file handle.

        :param cterasdk.objects.synchronous.core.Portal core: Portal object.
        """
        with fs.handle(path) as param:
            return await core.io.download(param)
    return wrapper


def handle_many(directory, *objects):
    """
    Create function to retrieve zip archive

    :param cterasdk.cio.edge.CorePath directory: Path to directory.
    :param args objects: List of files and folders.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    async def wrapper(core):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.core.Portal core: Portal object.
        :param str name: File name.
        :param object handle: File handle.
        """
        with fs.handle_many(directory, objects) as param:
            _, resource = await ensure_directory(core, directory)
            return await core.io.download_zip(str(resource.cloudFolderInfo.uid), encode_request_parameter(param))
    return wrapper


async def _validate_destination(core, name, destination):
    is_dir, resource = await ensure_directory(core, destination, suppress_error=True)
    if not is_dir:
        is_dir, resource = await ensure_directory(core, destination.parent)
        return resource.cloudFolderInfo.uid, destination.name, destination.parent
    return resource.cloudFolderInfo.uid, name, destination


def upload(name, size, destination, fd):
    """
    Create upload function

    :param str name: File name.
    :param cterasdk.cio.core.CorePath destination: Path to directory.
    :param object fd: File handle.
    :returns: Callable function to start the upload.
    :rtype: callable
    """
    async def wrapper(core):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.core.Portal core: Portal object.
        """
        uid, filename, directory = await _validate_destination(core, name, destination)
        with fs.upload(core, filename, directory, size, fd) as param:
            return await core.io.upload(str(uid), param)
    return wrapper


async def public_link(core, path, access, expire_in):
    with fs.public_link(path, access, expire_in) as param:
        response = await core.v1.api.execute('', 'createShare', param)
    return response.publicLink
