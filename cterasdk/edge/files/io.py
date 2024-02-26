import logging
from . import common


def mkdir(edge, path):
    logging.getLogger().info('Creating directory. %s', {'path': path.fullpath()})
    response = edge.webdav.mkcol(path.fullpath())
    common.raise_for_status(response, str(path.fullpath()))
    logging.getLogger().info('Directory created. %s', {'path': path.fullpath()})


def makedirs(edge, path):
    directories = path.parts()
    for i in range(1, len(directories) + 1):
        path = common.get_object_path(path.base, '/'.join(directories[:i]))
        try:
            mkdir(edge, path)
        except common.ItemExists:
            pass


def copy(edge, path, destination=None, overwrite=False):
    destination = destination.joinpath(path.name()).fullpath()
    logging.getLogger().info('Copying. %s', {'from': path.fullpath(), 'to': destination})
    edge.webdav.copy(path.fullpath(), destination, overwrite=overwrite)
    logging.getLogger().info('Copied. %s', {'from': path.fullpath(), 'to': destination})


def move(edge, path, destination=None, overwrite=False):
    destination = destination.joinpath(path.name()).fullpath()
    logging.getLogger().info('Moving. %s', {'from': path.fullpath(), 'to': destination})
    edge.webdav.move(path.fullpath(), destination, overwrite=overwrite)
    logging.getLogger().info('Moved. %s', {'from': path.fullpath(), 'to': destination})


def remove(edge, *paths):
    for path in paths:
        logging.getLogger().info('Deleting object. %s', {'path': path.fullpath()})
        edge.webdav.delete(path.fullpath())
        logging.getLogger().info('Object deleted. %s', {'path': path.fullpath()})
