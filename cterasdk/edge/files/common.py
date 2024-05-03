import logging
from pathlib import PurePosixPath
from ...exceptions import CTERAException
from ...objects import uri


class Path:

    def __init__(self, relative, base):
        self._base = PurePosixPath(base)
        self._relative = PurePosixPath(relative)
        if self._base.joinpath(self._relative) == self._relative:
            raise ValueError('You must specify a relative path. Omit leading / characters')

    @property
    def base(self):
        return self._base

    @property
    def relative(self):
        return self._relative

    def name(self):
        return self.relative.name

    def parent(self):
        return Path(str(self.relative.parent), str(self.base))

    def fullpath(self):
        return str(self.base.joinpath(self.relative))

    def encoded_fullpath(self):
        return uri.quote(self.fullpath())

    def encoded_parent(self):
        return uri.quote(str(self.parent()))

    def joinpath(self, path):
        return Path(str(self.relative.joinpath(path)), str(self.base))

    def parts(self):
        return self.relative.parts

    def __str__(self):
        return self.fullpath()


class ItemExists(CTERAException):
    """Already exists"""


class Forbidden(CTERAException):
    """Forbidden"""


def raise_for_status(response, path):
    error = {
        "File exists": ItemExists(),
        "Creating a folder in this location is forbidden": Forbidden(),
    }.get(response, None)
    try:
        if error:
            raise error
    except ItemExists as error:
        logging.getLogger('cterasdk.edge').warning('A file or folder with the same name already exists. %s', {'path': path})
        raise error
    except Forbidden as error:
        logging.getLogger('cterasdk.edge').error('Creating a folder in this location is forbidden. %s', {'name': path})
        raise error


def get_object_path(base, relative):
    return Path(relative, base)
