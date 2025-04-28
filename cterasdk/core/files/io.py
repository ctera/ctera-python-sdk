import logging
from ...cio import core as fs
from ...cio import exceptions
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
            logger.debug(f'Resource already exists: {path.reference.as_posix()}')


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
