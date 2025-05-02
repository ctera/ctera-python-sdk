import logging
from contextlib import contextmanager
from ..common import Object
from . import common, exceptions


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
    logger.info('Listing directory: %s', path)
    yield param


@contextmanager
def makedir(path):
    directory = path.absolute
    logger.info('Creating directory: %s', path.absolute)
    try:
        yield path.absolute
    except exceptions.CTERAException as error:
        try:
            accept_response(error.response.message.msg, directory)
        except exceptions.ResourceExistsError:
            logger.info('Directory already exists: %s', directory)
    logger.info('Directory created: %s', directory)


@contextmanager
def copy(path, destination):
    destination = destination.join(path.name).absolute
    logger.info('Copying: %s to: %s', path.absolute, destination)
    yield path.absolute, destination


@contextmanager
def move(path, destination):
    destination = destination.join(path.name).absolute
    logger.info('Moving: %s to: %s', path.absolute, destination)
    yield path.absolute, destination


def delete_generator(*paths):
    for path in paths:
        logger.info('Deleting item: %s', path.absolute)
        yield path


@contextmanager
def handle(path):
    logger.info('Getting file handle: %s', path.reference)
    yield path.absolute


@contextmanager
def handle_many(directory, objects):
    param = Object()
    param.paths = ['/'.join([directory.absolute, item]) for item in objects]
    param.snapshot = Object()
    param._classname = 'BackupRepository'  # pylint: disable=protected-access
    param.snapshot.location = 1
    param.snapshot.timestamp = None
    param.snapshot.path = None
    logger.info('Getting directory handle: %s', directory.reference)
    yield param


@contextmanager
def upload(name, destination, fd):
    param = dict(
        name=name,
        fullpath=f'{destination.absolute}/{name}',
        filedata=fd
    )
    logger.info('Uploading: %s to: %s', name, destination.reference)
    yield param


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
