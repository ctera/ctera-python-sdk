import logging

from ...exception import CTERAException
from .path import CTERAPath


class ItemExists(CTERAException):
    pass


class Forbidden(CTERAException):
    pass


CreateDirectoryRC = {
    "File exists": ItemExists,
    "Creating a folder in this location is forbidden": Forbidden
}


def mkdir(ctera_host, path, recurse=False):
    if recurse:
        array = path.parts()
        for i in range(1, len(array) + 1):
            dirpath = CTERAPath('/'.join(array[:i]), path.basepath)
            try:
                _mkdir(ctera_host, dirpath)
            except (ItemExists, Forbidden):
                pass
    else:
        _mkdir(ctera_host, path)


def _mkdir(ctera_host, path):
    fullpath = path.fullpath()
    logging.getLogger().info('Creating directory. %s', {'path': fullpath})
    try:
        ctera_host.mkcol(ctera_host.make_local_files_dir(fullpath), use_file_url=True)
    except CTERAException as error:
        _process_error(error, fullpath)
    logging.getLogger().info('Directory created. %s', {'path': fullpath})


def _process_error(error, path):
    if hasattr(error.response.body, 'msg'):
        message = error.response.body.msg
        error = CreateDirectoryRC.get(message)
        if error is not None:
            error = error()
            error.message = message
            error.path = path
            raise error
