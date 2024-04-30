import re
import logging

from pathlib import PurePosixPath

from .. import query
from ...lib import FetchResourcesResponse
from ...common import Object
from ...objects import uri
from ...exceptions import RemoteDirectoryNotFound, CTERAException


class ItemExists(CTERAException):
    """Already exists"""


class InvalidPath(CTERAException):
    """Invalid directory path"""


class InvalidName(CTERAException):
    """Invalid directory name"""


class ReservedName(CTERAException):
    """Reserved name"""


class SrcDstParam(Object):

    __instance = None

    @staticmethod
    def instance(src, dest=None):
        SrcDstParam(src, dest)
        return SrcDstParam.__instance

    def __init__(self, src, dest=None):
        self._classname = self.__class__.__name__
        self.src = src
        self.dest = dest
        SrcDstParam.__instance = self  # pylint: disable=unused-private-member


class ActionResourcesParam(Object):

    __instance = None

    @staticmethod
    def instance():
        ActionResourcesParam()
        return ActionResourcesParam.__instance

    def __init__(self):
        self._classname = self.__class__.__name__
        self.urls = []
        ActionResourcesParam.__instance = self  # pylint: disable=unused-private-member

    def add(self, param):
        self.urls.append(param)


class CreateShareParam(Object):

    __instance = None

    @staticmethod
    def instance(path, access, expire_on):
        CreateShareParam(path, access, expire_on)
        return CreateShareParam.__instance

    def __init__(self, path, access, expire_on):
        self._classname = self.__class__.__name__
        self.url = path
        self.share = Object()
        self.share._classname = 'ShareConfig'
        self.share.accessMode = access
        self.share.protectionLevel = 'publicLink'
        self.share.expiration = expire_on
        self.share.invitee = Object()
        self.share.invitee._classname = 'Collaborator'
        self.share.invitee.type = 'external'
        CreateShareParam.__instance = self  # pylint: disable=unused-private-member


class FetchResourcesParam(Object):

    def __init__(self):
        self._classname = 'FetchResourcesParam'
        self.start = 0
        self.limit = 100

    def increment(self):
        self.start = self.start + self.limit


class FetchResourcesParamBuilder:

    def __init__(self):
        self.param = FetchResourcesParam()

    def root(self, root):
        self.param.root = root  # pylint: disable=attribute-defined-outside-init
        return self

    def depth(self, depth):
        self.param.depth = depth  # pylint: disable=attribute-defined-outside-init
        return self

    def include_deleted(self):
        self.param.includeDeleted = True  # pylint: disable=attribute-defined-outside-init

    def build(self):
        return self.param


class Path:

    def __init__(self, param, base):
        self._base = PurePosixPath(base)
        self._relative = PurePosixPath()
        if Path._is_server_object(param):
            self._from_server_object(param)
        elif isinstance(param, str):
            self._from_string(param)
        else:
            message = 'Invalid directory path specified. Please ensure the directory path is correct and try again.'
            logging.getLogger('cterasdk.core').error(message)
            raise ValueError(message)

        if self._relative.root == '/' or self._base.joinpath(self._relative) == self._relative:
            raise ValueError('You must specify a relative path. Omit leading / characters')

    @staticmethod
    def _is_server_object(param):
        return isinstance(param, Object) and param.__dict__.get('_classname', None) == 'ResourceInfo'

    def _from_server_object(self, param):
        href = uri.unquote(param.href)
        match = re.search('^/(ServicesPortal|admin)/webdav', href)
        start, end = match.span()
        self._base = self._base.joinpath(href[start: end])
        self._relative = self._relative.joinpath(href[end + 1:])

    def _from_string(self, param):
        self._relative = self._relative.joinpath(param)

    def name(self):
        return self._relative.name

    @property
    def base(self):
        return str(self._base)

    @property
    def relative(self):
        return self._relative

    def parent(self):
        return Path(str(self._relative.parent), str(self._base))

    def fullpath(self):
        return str(self._base.joinpath(self._relative))

    def encoded_fullpath(self):
        return uri.quote(self.fullpath())

    def encoded_parent(self):
        return uri.quote(str(self.parent()))

    def joinpath(self, path):
        return Path(str(self._relative.joinpath(path)), str(self._base))

    def parts(self):
        return self._relative.parts

    def __str__(self):
        return self.fullpath()


def fetch_resources(core, param):
    return core.api.execute('', 'fetchResources', param)


def objects_iterator(core, param):
    return query.iterator(core, '', param, 'fetchResources', callback_response=FetchResourcesResponse)


def get_resource_info(core, path):
    response = core.files.listdir(str(path.relative), depth=0)
    if response.root is None:
        raise RemoteDirectoryNotFound(path.fullpath())
    return response.root


def get_object_path(base, elements):
    if isinstance(elements, list):
        return [Path(element, base) for element in elements]
    return Path(elements, base)


def get_create_dir_param(name, parent):
    param = Object()
    param.name = name
    param.parentPath = parent
    return param


def raise_for_status(response, path):
    error = {
        "FileWithTheSameNameExist": ItemExists(),
        "DestinationNotExists": InvalidPath(),
        "InvalidName": InvalidName(),
        "ReservedName": ReservedName()
    }.get(response, None)
    try:
        if error:
            raise error
    except ItemExists as error:
        logging.getLogger('cterasdk.core').info('A file or folder with the same name already exists. %s', {'path': path})
        raise error
    except InvalidPath as error:
        logging.getLogger('cterasdk.core').error('Invalid parent directory path. %s', {'path': path})
        raise error
    except InvalidName as error:
        logging.getLogger('cterasdk.core').error('Directory name contains invalid characters. %s', {'name': path})
        raise error
    except ReservedName as error:
        logging.getLogger('cterasdk.core').error('Reserved directory name. %s', {'name': path})
        raise error
