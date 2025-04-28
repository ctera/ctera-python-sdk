import logging
from ..common import Object
from . import common, exceptions
from contextlib import contextmanager


logger = logging.getLogger('cterasdk.edge')


class EdgePath(common.BasePath):
    """Path for CTERA Edge Filer"""

    @staticmethod
    def instance(scope, reference):
        return EdgePath(scope, reference)


@contextmanager
def listdir(path):
    param = Object()
    param.path = path
    logger.info(f'Listing directory: {path}')
    yield param


@contextmanager
def makedir(path):
    directory = path.absolute
    logger.info('Creating directory. %s', {'path': path.absolute})
    try:
        yield path.absolute
    except exceptions.CTERAException as error:
        try:
            accept_response(error.response.message.msg, directory)
        except exceptions.ResourceExistsError:
            logger.info('Directory already exists. %s', {'path': directory})
    logger.info('Directory created. %s', {'path': directory})


@contextmanager
def copy(path, destination):
    destination = destination.join(path.name).absolute
    logger.info(f'Copying: {path.absolute} to: {destination}')
    yield path.absolute, destination


@contextmanager
def move(path, destination):
    destination = destination.join(path.name).absolute
    logger.info(f'Moving: {path.absolute} to: {destination}')
    yield path.absolute, destination


def delete_generator(*paths):
    for path in paths:
        logger.info(f'Deleting item: {path.absolute}')
        yield path


def accept_response(response, reference):
    error = {
        "File exists": exceptions.ResourceExistsError(),
        "Creating a folder in this location is forbidden": exceptions.RestrictedPathError(),
    }.get(response, None)
    try:
        if error:
            raise error
    except exceptions.ResourceExistsError as error:
        logger.warning('Resource already exists: a file or folder with this name already exists. %s', {'path': reference})
        raise error
    except exceptions.RestrictedPathError as error:
        logger.error('Creating a folder in the specified location is forbidden. %s', {'name': reference})
        raise error
