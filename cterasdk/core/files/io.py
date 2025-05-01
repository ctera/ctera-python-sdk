import logging
from ...cio.common import encode_request_parameter
from ...cio import core as fs
from ...cio import exceptions
from ...common import Object
from ... import query
from ...lib import FetchResourcesResponse


logger = logging.getLogger('cterasdk.core')


def listdir(core, path, depth=None, include_deleted=False, search_criteria=None, limit=None):
    with fs.fetch_resources(path, depth, include_deleted, search_criteria, limit) as param:
        if param.depth > 0:
            return query.iterator(core, '', param, 'fetchResources', callback_response=FetchResourcesResponse)
        return core.api.execute('', 'fetchResources', param)


def root(core, path):
    response = listdir(core, path, 0)
    if response.root is None:
        raise exceptions.RemoteStorageException(path.absolute)
    return response.root


def versions(core, path):
    with fs.versions(path):
        return core.api.execute('', 'listSnapshots', path.absolute)


def walk(core, scope, path, include_deleted=False):
    paths = [fs.CorePath.instance(scope, path)]
    while len(paths) > 0:
        path = paths.pop(0)
        entries = listdir(core, path, include_deleted=include_deleted)
        for e in entries:
            if e.isFolder:
                paths.append(fs.CorePath.instance(scope, e))
            yield e


def mkdir(core, path):
    with fs.makedir(path) as param:
        response = core.api.execute('', 'makeCollection', param)
    fs.accept_response(response, path.reference.as_posix())


def makedirs(core, path):
    directories = path.parts
    for i in range(1, len(directories) + 1):
        path = fs.CorePath.instance(path.scope, '/'.join(directories[:i]))
        try:
            mkdir(core, path)
        except exceptions.ResourceExistsError:
            logger.debug('Resource already exists: %s', path.reference.as_posix())


def rename(core, path, name):
    with fs.rename(path, name) as param:
        return core.api.execute('', 'moveResources', param)


def remove(core, *paths):
    with fs.delete(*paths) as param:
        return core.api.execute('', 'deleteResources', param)


def recover(core, *paths):
    with fs.recover(*paths) as param:
        return core.api.execute('', 'restoreResources', param)


def copy(core, *paths, destination=None):
    with fs.copy(*paths, destination=destination) as param:
        return core.api.execute('', 'copyResources', param)


def move(core, *paths, destination=None):
    with fs.move(*paths, destination=destination) as param:
        return core.api.execute('', 'moveResources', param)


def retrieve_remote_dir(core, directory):
    resource = root(core, directory)
    if not resource.isFolder:
        raise exceptions.RemoteStorageException('The destination path is not a directory', None, path=directory.absolute)
    return str(resource.cloudFolderInfo.uid)


def handle(path):
    """
    Create function to retrieve file handle.

    :param cterasdk.cio.edge.CorePath path: Path to file.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    def wrapper(core):
        """
        Get file handle.

        :param cterasdk.objects.synchronous.core.Portal core: Portal object.
        """
        logger.info('Getting file handle: %s', path.reference)
        return core.io.download(path.reference)
    return wrapper


def handle_many(directory, *objects):
    """
    Create function to retrieve zip archive

    :param cterasdk.cio.edge.CorePath directory: Path to directory.
    :param *str objects: List of files and folders.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    def wrapper(core):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.core.Portal core: Portal object.
        :param str name: File name.
        :param object handle: File handle.
        """
        param = Object()
        param.paths = ['/'.join([directory.absolute, filename]) for filename in objects]
        param.snapshot = None
        param.password = None
        param.portalName = None
        param.showDeleted = False
        logger.info('Getting directory handle: %s', directory.reference)
        return core.io.download_zip(retrieve_remote_dir(core, directory), encode_request_parameter(param))
    return wrapper


def upload(name, size, destination, handle):
    """
    Create upload function

    :param str name: File name.
    :param cterasdk.cio.core.CorePath destination: Path to directory.
    :param object handle: File handle.
    :returns: Callable function to start the upload.
    :rtype: callable
    """
    def wrapper(core):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.core.Portal core: POrtal object.
        """
        param = dict(
            name=name,
            Filename=name,
            fullpath=core.io.builder(fs.CorePath(destination.reference, name).absolute_encode),
            fileSize=size,
            file=handle
        )
        target = retrieve_remote_dir(core, destination)
        logger.info('Uploading: %s to: %s', name, destination.reference)
        return core.io.upload(target, param)
    return wrapper
