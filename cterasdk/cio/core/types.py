import re
import urllib.parse
from datetime import datetime
from ...common import Object
from ..common import BasePath, BaseResource
from ...lib.iterator import DefaultResponse


class PortalPath(BasePath):

    @staticmethod
    def from_server_object(server_object):
        """
        Parse Path from Server Object.

        :param object server_object: Server Object
        """
        classname = getattr(server_object, '_classname', None)

        if classname == 'ResourceInfo':
            return PortalPath.from_resource(server_object)

        if classname == 'SnapshotResp':
            return PortalPath.from_snapshot(server_object)

        if classname == 'ResourceActionCursor':
            return PortalPath.from_cursor(server_object)

        raise ValueError(f"Unsupported server object type: '{classname}'")

    @staticmethod
    def from_resource(resource):
        """
        Create Path Object from 'ResourceInfo' Class Object.

        :param object resource: Resource Info Object
        """
        return PortalPath.from_str(urllib.parse.unquote(resource.href))

    @staticmethod
    def from_snapshot(snapshot):
        """
        Create Path Object from 'SnapshotResp' Class Object.

        :param object snapshot: Snapshot Response Object
        """
        return PortalPath.from_str(urllib.parse.unquote(snapshot.url + snapshot.path))

    @staticmethod
    def from_cursor(cursor):
        """
        Create Path Object from 'ResourceActionCursor' Class Object.

        :param object cursor: Resource Action Cursor Object
        """
        return PortalPath.from_str(urllib.parse.unquote(cursor.upperLevelUrl))

    @staticmethod
    def from_str(path):
        """
        Create Path Object from String.

        :param str path: Path
        """
        return PortalPath._parse_from_str(path or '')

    @staticmethod
    def _parse_from_str(path):
        """
        Path Object from String.

        :param str path: Path
        """
        groups = [f'(?P<{o.__name__}>{namespace})' for namespace, o in Namespaces.items()]
        regex = re.compile(f"^{'|'.join(groups)}")
        match = re.match(regex, path)
        if match:
            return Namespaces[match.group()](path[match.end():])
        raise ValueError(f'Could not determine object path: {path}')


class ServicesPortalPath(PortalPath):
    """
    ServicesPortal Path Object
    """
    Namespace = '/ServicesPortal/webdav'

    def __init__(self, reference):
        super().__init__(ServicesPortalPath.Namespace, reference)


class GlobalAdminPath(PortalPath):
    """
    Global Admin Path Object
    """
    Namespace = '/admin/webdav'

    def __init__(self, reference):
        super().__init__(GlobalAdminPath.Namespace, reference)


Namespaces = {
    ServicesPortalPath.Namespace: ServicesPortalPath,
    GlobalAdminPath.Namespace: GlobalAdminPath
}


def resolve(path, namespace=None):
    """
    Resolve Path

    :param object path: Path
    :param cterasdk.cio.core.types.PortalPath,optional namespace: Path Object
    """
    if isinstance(path, PortalPath):
        return path

    if isinstance(path, (PortalResource, PreviousVersion)):
        return path.path

    if isinstance(path, Object):
        return PortalPath.from_server_object(path)

    if namespace:
        if path is None or isinstance(path, str):
            return namespace(path or '')

    raise ValueError(f'Error: Could not resolve path: {path}. Type: {type(path)}')


def create_generator(paths, namespace=None):
    """
    Create Path Object Generator Object.

    :param object paths: List or a tuple
    :param cterasdk.cio.core.types.PortalPath,optional namespace: Path Object
    """
    def wrapper():
        for path in paths:
            if isinstance(path, tuple):
                yield resolve(path[0], namespace), resolve(path[1], namespace)
            else:
                yield resolve(path, namespace)
    return wrapper()


def automatic_resolution(p, context=None):
    """
    Automatic Resolution of Path Object

    :param object p: Path
    :param str,optional context: Context (e.g. 'ServicesPortal' or 'admin')
    """
    namespace = Namespaces.get(f'/{context}/webdav', None)

    if isinstance(p, (list, tuple)):
        return create_generator(p, namespace)

    return resolve(p, namespace)


class SrcDstParam(Object):

    __instance = None

    @staticmethod
    def instance(src, dest=None):
        SrcDstParam(src, dest)
        return SrcDstParam.__instance

    def __init__(self, src, dest=None):
        super().__init__()
        self._classname = self.__class__.__name__
        self.src = src
        self.dest = dest
        SrcDstParam.__instance = self  # pylint: disable=unused-private-member


class ResourceActionCursor(Object):

    def __init__(self):
        super().__init__()
        self._classname = self.__class__.__name__


class ActionResourcesParam(Object):

    __instance = None

    @staticmethod
    def instance():
        ActionResourcesParam()
        return ActionResourcesParam.__instance

    def __init__(self):
        super().__init__()
        self._classname = self.__class__.__name__
        self.urls = []
        self.startFrom = None
        ActionResourcesParam.__instance = self  # pylint: disable=unused-private-member

    def add(self, param):
        self.urls.append(param)

    def start_from(self, cursor):
        self.startFrom = cursor


class CreateShareParam(Object):

    __instance = None

    @staticmethod
    def instance(path, access, expire_on):
        CreateShareParam(path, access, expire_on)
        return CreateShareParam.__instance

    def __init__(self, path, access, expire_on):
        super().__init__()
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
        super().__init__()
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

    def searchCriteria(self, criteria):
        self.param.searchCriteria = criteria  # pylint: disable=attribute-defined-outside-init
        return self

    def include_deleted(self):
        self.param.includeDeleted = True  # pylint: disable=attribute-defined-outside-init
        return self

    def limit(self, limit):
        self.param.limit = limit
        return self

    def build(self):
        return self.param


class FetchResourcesError(Exception):

    def __init__(self, error):
        super().__init__()
        self.error = error


class FetchResourcesResponse(DefaultResponse):

    def __init__(self, response):
        super().__init__(response)
        if response.errorType is not None:
            raise FetchResourcesError(response.errorType)

    @property
    def objects(self):
        return self._response.items


class VolumeOwner(Object):
    """
    Class for a Cloud Volume Owner.

    :ivar int id: Owner ID
    :ivar str id: Owner Full Name.
    :ivar str namespace: User namespace.
    """
    def __init__(self, i, name):
        super().__init__(id=i, name=name)

    @property
    def user_namespace(self):
        return f'/Users/{self.name}'


class PortalVolume(Object):
    """
    Class for a Portal Cloud Volume.

    :ivar int id: Cloud Drive Folder ID
    :ivar str name: Cloud Drive Folder Name
    :ivar int group: Folder Group ID
    :ivar bool protected: Passphrase-Protected
    :ivar cterasdk.core.types.VolumeOwner owner: Volume owner information.
    """
    def __init__(self, i, name, group, protected, owner):
        super().__init__(id=i, name=name, group=group, protected=protected, owner=owner)

    @staticmethod
    def from_server_object(server_object):
        return PortalVolume(
            server_object.uid,
            server_object.name,
            server_object.groupUid,
            server_object.passphraseProtected,
            VolumeOwner(server_object.ownerUid, server_object.ownerFriendlyName)
        )


class PreviousVersion(Object):
    """
    Class Representing a Previous Version

    :ivar bool current: Current
    :ivar cterasdk.cio.types.PortalPath path: Path Object
    :ivar datetime.datetime start_time: Snapshot start time
    :ivar datetime.datetime end_time: Snapshot end time
    """
    def __init__(self, server_object):
        super().__init__(
            path=PortalPath.from_snapshot(server_object),
            current=server_object.current,
            start_time=datetime.fromisoformat(server_object.startTimestamp),
            end_time=datetime.fromisoformat(server_object.calculatedTimestamp)
        )

    @staticmethod
    def from_server_object(server_object):
        return PreviousVersion(server_object)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"{{'start_time': {self.start_time.isoformat()}, "
            f"'end_time': {self.end_time.isoformat()}, "
            f"'current': {self.current}, "
            f"'path': {self.path}}})"
        )


class PortalResource(BaseResource):
    """
    Class for a Portal Filesystem Resource.

    :ivar int,optional id: Resource ID, defaults to ``None`` if not exists
    :ivar str name: Resource name
    :ivar cterasdk.cio.types.PortalPath path: Path Object
    :ivar bool is_dir: ``True`` if directory, ``False`` otherwise
    :ivar bool deleted: ``True`` if deleted, ``False`` otherwise
    :ivar int size: Size
    :ivar datetime.datetime last_modified: Last Modified
    :ivar str extension: Extension
    :ivar str permalink: Permalink
    :ivar cterasdk.core.types.Volume,optional volume: Volume information.
    """
    def __init__(self, i, name, path, is_dir, deleted, size, permalink, last_modified, volume):
        super().__init__(
            name, path, is_dir, size,
            None if last_modified is None else datetime.fromisoformat(last_modified),
        )
        self.id = i
        self.deleted = deleted
        self.permalink = permalink
        self.volume = PortalVolume.from_server_object(volume) if volume else None

    @staticmethod
    def from_server_object(server_object):
        return PortalResource(
            getattr(server_object, 'fileId', None),
            server_object.name,
            PortalPath.from_resource(server_object),
            server_object.isFolder,
            server_object.isDeleted,
            server_object.size,
            server_object.permalink,
            server_object.lastmodified,
            server_object.cloudFolderInfo
        )

    @property
    def with_user_namespace(self):
        return PortalPath(self.volume.owner.user_namespace if self.volume else '/', self.path.relative).absolute
