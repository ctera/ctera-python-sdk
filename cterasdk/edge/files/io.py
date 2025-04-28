import logging
from ...exceptions import CTERAException
from ...cio import edge as edge_parameters
from ...cio import exceptions


def listdir(edge, path):
    param = edge_parameters.create_listdir_parameter(path)
    return edge.api.execute('/status/fileManager', 'listPhysicalFolders', param)


def mkdir(edge, path):
    directory = path.absolute
    logging.getLogger('cterasdk.edge').info('Creating directory. %s', {'path': directory})
    try:
        edge.io.mkdir(path.absolute)
    except CTERAException as error:
        try:
            edge_parameters.raise_for_status(error.response.message.msg, directory)
        except exceptions.ResourceExistsError:
            logging.getLogger('cterasdk.edge').info('Directory already exists. %s', {'path': directory})
    logging.getLogger('cterasdk.edge').info('Directory created. %s', {'path': directory})
    return directory


def makedirs(edge, path):
    directories = path.parts()
    for i in range(1, len(directories) + 1):
        path = edge_parameters.EdgePath(path.scope, '/'.join(directories[:i]))
        try:
            mkdir(edge, path)
        except exceptions.RestrictedPathError:
            pass


def copy(edge, path, destination=None, overwrite=False):
    destination = destination.join(path.name).absolute
    logging.getLogger('cterasdk.edge').info('Copying. %s', {'from': path.absolute, 'to': destination})
    edge.io.copy(path.absolute, destination, overwrite=overwrite)
    logging.getLogger('cterasdk.edge').info('Copied. %s', {'from': path.absolute, 'to': destination})


def move(edge, path, destination=None, overwrite=False):
    destination = destination.join(path.name).absolute
    logging.getLogger('cterasdk.edge').info('Moving. %s', {'from': path.absolute, 'to': destination})
    edge.io.move(path.absolute, destination, overwrite=overwrite)
    logging.getLogger('cterasdk.edge').info('Moved. %s', {'from': path.absolute, 'to': destination})


def remove(edge, *paths):
    for path in paths:
        logging.getLogger('cterasdk.edge').info('Deleting object. %s', {'path': path.absolute})
        edge.io.delete(path.absolute)
        logging.getLogger('cterasdk.edge').info('Object deleted. %s', {'path': path.absolute})
