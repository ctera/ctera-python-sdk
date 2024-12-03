import logging
from ...exceptions import CTERAException
from . import common


def mkdir(edge, path):
    directory = path.fullpath()
    logging.getLogger('cterasdk.edge').info('Creating directory. %s', {'path': directory})
    try:
        edge.io.mkdir(path.fullpath())
    except CTERAException as error:
        try:
            common.raise_for_status(error.response.message.msg, directory)
        except common.ItemExists:
            logging.getLogger('cterasdk.edge').info('Directory already exists. %s', {'path': directory})
    logging.getLogger('cterasdk.edge').info('Directory created. %s', {'path': directory})
    return directory


def makedirs(edge, path):
    directories = path.parts()
    for i in range(1, len(directories) + 1):
        path = common.get_object_path(path.base, '/'.join(directories[:i]))
        try:
            mkdir(edge, path)
        except common.Forbidden:
            pass


def copy(edge, path, destination=None, overwrite=False):
    destination = destination.joinpath(path.name()).fullpath()
    logging.getLogger('cterasdk.edge').info('Copying. %s', {'from': path.fullpath(), 'to': destination})
    edge.io.copy(path.fullpath(), destination, overwrite=overwrite)
    logging.getLogger('cterasdk.edge').info('Copied. %s', {'from': path.fullpath(), 'to': destination})


def move(edge, path, destination=None, overwrite=False):
    destination = destination.joinpath(path.name()).fullpath()
    logging.getLogger('cterasdk.edge').info('Moving. %s', {'from': path.fullpath(), 'to': destination})
    edge.io.move(path.fullpath(), destination, overwrite=overwrite)
    logging.getLogger('cterasdk.edge').info('Moved. %s', {'from': path.fullpath(), 'to': destination})


def remove(edge, *paths):
    for path in paths:
        logging.getLogger('cterasdk.edge').info('Deleting object. %s', {'path': path.fullpath()})
        edge.io.delete(path.fullpath())
        logging.getLogger('cterasdk.edge').info('Object deleted. %s', {'path': path.fullpath()})


def listdirs(edge, path):
    """
    List contents of a directory
    
    :param edge: Edge filer instance
    :param path: Path object representing the directory to list
    :returns: Directory listing response
    """
    logging.getLogger('cterasdk.edge').info('Listing directory. %s', {'path': path.fullpath()})
    try:
        param = edge.files._file_access._get_list_directory_param(path)
        response = edge.api.execute('/status/fileManager', 'listPhysicalFolders', param)
        logging.getLogger('cterasdk.edge').debug('Directory listed. %s', {'path': path.fullpath()})
        return response
    except CTERAException as error:
        logging.getLogger('cterasdk.edge').error('Failed to list directory. %s', {'path': path.fullpath()})
        raise error
