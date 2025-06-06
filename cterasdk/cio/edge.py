import logging
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
from ..common import Object
from ..objects.uri import unquote
from . import common
from ..exceptions.io import CTERAException, ResourceExistsError, RestrictedPathError


logger = logging.getLogger('cterasdk.edge')


class EdgePath(common.BasePath):
    """Path for CTERA Edge Filer"""

    def __init__(self, scope, reference):
        """
        Initialize a CTERA Edge Filer Path.

        :param str scope: Scope.
        :param str reference: Reference.
        """
        if isinstance(reference, Object):
            super().__init__(scope, reference.path)
        elif isinstance(reference, str):
            super().__init__(scope, reference)
        elif reference is None:
            super().__init__(scope, '')
        else:
            message = 'Path validation failed: ensure the path exists and is correctly formatted.'
            logger.error(message)
            raise ValueError(message)

    @staticmethod
    def instance(scope, reference):
        return EdgePath(scope, reference)


def fetch_reference(href):
    namespace = '/localFiles'
    return unquote(href[href.index(namespace)+len(namespace) + 1:])


def format_listdir_response(parent, response):
    entries = []
    for e in response:
        path = fetch_reference(e.href)
        if path and parent != path:
            is_dir = e.getcontenttype == 'httpd/unix-directory'
            param = Object(
                path=path,
                name=Path(path).name,
                is_dir=is_dir,
                is_file=not is_dir,
                created_at=e.creationdate,
                last_modified=datetime.strptime(e.getlastmodified, "%a, %d %b %Y %H:%M:%S GMT").isoformat(),
                size=e.getcontentlength
            )
            entries.append(param)
    return entries


@contextmanager
def makedir(path):
    directory = path.absolute
    logger.info('Creating directory: %s', path.absolute)
    try:
        yield path.absolute
    except CTERAException as error:
        try:
            accept_response(error.response.message.msg, directory)
        except ResourceExistsError:
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
    fd, *_ = common.encode_stream(fd, 0)
    param = dict(
        name=name,
        fullpath=f'{destination.absolute}/{name}',
        filedata=fd
    )
    logger.info('Uploading: %s to: %s', name, destination.reference)
    yield param


def accept_response(response, reference):
    error = {
        "File exists": ResourceExistsError(),
        "Creating a folder in this location is forbidden": RestrictedPathError(),
    }.get(response, None)
    try:
        if error:
            raise error
    except ResourceExistsError as error:
        logger.warning('Resource already exists: a file or folder with this name already exists. %s', {'path': reference})
        raise error
    except RestrictedPathError as error:
        logger.error('Creating a folder in the specified location is forbidden. %s', {'name': reference})
        raise error
