import logging
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
            logger.warning(f'Creating a folder in the specified location is forbidden: {path.reference.as_posix()}')


def copy(edge, path, destination=None, overwrite=False):
    with fs.copy(path, destination) as (path, destination):
        edge.io.copy(path, destination, overwrite=overwrite)


def move(edge, path, destination=None, overwrite=False):
    with fs.move(path, destination) as (path, destination):
        edge.io.move(path, destination, overwrite=overwrite)


def remove(edge, *paths):
    for path in fs.delete_generator(*paths):
        edge.io.delete(path.absolute)
