import re
import logging
import asyncio
from abc import abstractmethod
from ..objects.uri import quote, unquote
from ..common import Object, DateTimeUtils
from ..core.enum import ProtectionLevel, CollaboratorType, SearchType, PortalAccountType, FileAccessMode, \
    UploadError, ResourceScope, ResourceError
from ..core.types import PortalAccount, UserAccount, GroupAccount
from ..exceptions.io import PathValidationError, NameSyntaxError, \
    ReservedNameError, RestrictedRoot, PermissionDenied, FileConflict, NotADirectory, \
    UnwriteableScope
from ..exceptions.io import UploadException, QuotaViolation, RejectedByPolicy, NoStorageBucket, WindowsACLError, ResourceNotFoundError
from ..lib.iterator import DefaultResponse
from ..lib.storage import synfs, asynfs, commonfs
from . import common
from .actions import PortalCommand


logger = logging.getLogger('cterasdk.core')


class CorePath(common.BasePath):
    """Path for CTERA Portal"""

    def __init__(self, scope, reference):
        """
        Initialize a CTERA Portal Path.

        :param str scope: Scope.
        :param str reference: Reference.
        """
        if isinstance(reference, Object):
            super().__init__(*CorePath._from_server_object(reference))
        elif isinstance(reference, str):
            super().__init__(scope, reference)
        elif reference is None:
            super().__init__(scope, '')
        else:
            message = 'Path validation failed: ensure the path exists and is correctly formatted.'
            logger.error(message)
            raise ValueError(message)

    @staticmethod
    def _from_server_object(reference):
        """
        Parse Path from Server Object.

        :param object reference: Path.
        :returns: Base Path and Relative Path
        :rtype: tuple(str)
        """
        classname = reference.__dict__.get('_classname', None)

        href = None
        if classname == 'ResourceInfo':
            href = reference.href
        elif classname == 'SnapshotResp':
            href = f'{reference.url}{reference.path}'
        else:
            raise ValueError('Could not determine server object: {classname}')

        href = unquote(href)
        match = re.search('^/?(ServicesPortal|admin)/webdav', href)
        start, end = match.span()
        return (href[start: end], href[end + 1:])

    @property
    def absolute(self):
        reference = self.relative
        previous_versions = 'PreviousVersions/'
        if previous_versions in reference:
            index = reference.index(previous_versions) + len(previous_versions)
            return f'{self.scope.as_posix()}/{quote(reference[:index]) + reference[index:]}'
        return super().absolute

    @staticmethod
    def instance(scope, entries):
        if isinstance(entries, list):
            return [CorePath(scope, e) for e in entries]
        if isinstance(entries, tuple):
            source, destination = entries
            return (CorePath(scope, source), CorePath(scope, destination))
        return CorePath(scope, entries)


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


def destination_prerequisite_conditions(destination, name):
    if any(c in name for c in ['\\', '/', ':', '?', '&', '<', '>', '"', '|']):
        raise NameSyntaxError(destination.join(name).relative)


class EnsureDirectory(PortalCommand):

    def __init__(self, function, receiver, path, suppress_error=False):
        super().__init__(function, receiver)
        self.path = path
        self.suppress_error = suppress_error

    def _execute(self):
        return GetMetadata(self._function, self._receiver, self.path, self.suppress_error).execute()

    async def _a_execute(self):
        return await GetMetadata(self._function, self._receiver, self.path, self.suppress_error).a_execute()

    def _handle_response(self, r):
        exists, resource = r
        if (not exists or not resource.isFolder) and not self.suppress_error:
            raise NotADirectory(self.path.relative)
        return resource.isFolder if exists else False, resource


def ensure_writeable(resource, directory):
    if resource.scope == ResourceScope.Root:
        raise RestrictedRoot()
    if resource.scope not in [ResourceScope.Personal, ResourceScope.Project, ResourceScope.InsideCloudFolder]:
        raise UnwriteableScope(directory.relative, resource.scope)
    if resource.permission != FileAccessMode.RW:
        raise PermissionDenied(directory.relative)


class Upload(PortalCommand):

    def __init__(self, function, receiver, metadata_function, name, destination, size, fd):
        super().__init__(function, receiver)
        destination_prerequisite_conditions(destination, name)
        self.metadata_function = metadata_function
        self.name = name
        self.destination = destination
        self.size = size
        self.fd = fd

    def get_parameter(self):
        fd, size = common.encode_stream(self.fd, self.size)
        param = dict(
            name=self.name,
            Filename=self.name,
            fullpath=self._receiver.io.builder(CorePath(self.destination.reference, self.name).absolute_encode),
            fileSize=size,
            file=fd
        )
        return param

    def _validate_destination(self):
        is_dir, resource = EnsureDirectory(self.metadata_function, self._receiver, self.destination, True).execute()
        if not is_dir:
            is_dir, resource = EnsureDirectory(self.metadata_function, self._receiver, self.destination.parent).execute()
            self.name, self.destination = self.destination.name, self.destination.parent
        ensure_writeable(resource, self.destination)
        return resource.cloudFolderInfo.uid

    async def _a_validate_destination(self):
        is_dir, resource = await EnsureDirectory(self.metadata_function, self._receiver, self.destination, True).a_execute()
        if not is_dir:
            is_dir, resource = await EnsureDirectory(self.metadata_function, self._receiver, self.destination.parent).a_execute()
            self.name, self.destination = self.destination.name, self.destination.parent
        ensure_writeable(resource, self.destination)
        return resource.cloudFolderInfo.uid

    def _before_command(self):
        logger.info('Uploading: %s', self.destination.join(self.name).relative)

    def _execute(self):
        cloudfolder = self._validate_destination()
        with self.trace_execution():
            return self._function(self._receiver, str(cloudfolder), self.get_parameter())

    def _handle_response(self, r):
        path = self.destination.join(self.name).relative
        if r.rc:
            logger.error('Upload failed: %s', path)
            if r.msg == UploadError.UserQuotaViolation:
                raise QuotaViolation('User', path)
            if r.msg == UploadError.PortalQuotaViolation:
                raise QuotaViolation('Team Portal', path)
            if r.msg == UploadError.FolderQuotaViolation:
                raise QuotaViolation('Cloud drive folder', path)
            if r.msg == UploadError.RejectedByPolicy:
                raise RejectedByPolicy(path)
            if r.msg == UploadError.WindowsACL:
                raise WindowsACLError(path)
            if r.msg.startswith(UploadError.NoStorageBucket):
                raise NoStorageBucket(path)
            raise UploadException(f'Reason: {r.msg}', path)
        if not r.rc and r.msg == 'OK':
            logger.info('Upload success. Saved to: %s', path)
        return path

    async def _a_execute(self):
        cloudfolder = await self._a_validate_destination()
        with self.trace_execution():
            return await self._function(self._receiver, str(cloudfolder), self.get_parameter())


class UploadFile(PortalCommand):

    def __init__(self, function, receiver, metadata_function, path, destination):
        super().__init__(function, receiver)
        self._metadata_function = metadata_function
        self.path = path
        self.destination = destination

    def _get_properties(self):
        return commonfs.properties(self.path)

    def _execute(self):
        metadata = self._get_properties()
        with open(self.path, 'rb') as handle:
            with self.trace_execution():
                return Upload(self._function, self._receiver, self._metadata_function, metadata['name'],
                              self.destination, metadata['size'], handle).execute()

    async def _a_execute(self):
        metadata = self._get_properties()
        with open(self.path, 'rb') as handle:
            with self.trace_execution():
                return await Upload(self._function, self._receiver, self._metadata_function, metadata['name'],
                              self.destination, metadata['size'], handle).a_execute()


def _is_sharing_on_user_behalf(path):
    return re.match(r'^Users/[^/]+(?=/)', path.relative) is not None


def _is_subfolder(path):
    depth = len(path.reference.parts)
    sharing_on_user_behalf = _is_sharing_on_user_behalf(path)
    return (sharing_on_user_behalf and depth > 3) or (not sharing_on_user_behalf and depth > 1)


def create_share_parameter(path, as_project, allow_reshare, allow_sync, shares=None):
    if _is_subfolder(path):
        as_project = False  # Can't be a team project
        allow_sync = False  # Can't allow sync of a sub-folder

    param = Object()
    param._classname = 'ShareResourceParam'  # pylint: disable=protected-access
    param.url = path.absolute_encode
    param.teamProject = as_project
    param.allowReshare = allow_reshare
    param.shouldSync = allow_sync
    param.shares = []
    if shares is not None:
        for recipient in shares:
            settings = Object()
            settings._classname = 'ShareConfig'  # pylint: disable=protected-access
            settings.accessMode = recipient.accessMode
            settings.expiration = recipient.expiration
            settings.protectionLevel = recipient.protectionLevel
            settings.invitee = recipient.invitee
            param.shares.append(settings)
    return param


def add_share_recipient(param, recipient):
    settings = Object()
    settings._classname = 'ShareConfig'  # pylint: disable=protected-access
    settings.accessMode = recipient.access
    if not recipient.access == FileAccessMode.NA:
        settings.expiration = recipient.expiration_date
    invitee = None
    if recipient.type == CollaboratorType.EXT:
        invitee = Object()
        invitee._classname = 'Collaborator'  # pylint: disable=protected-access
        invitee.type = recipient.type
        invitee.email = recipient.account
        if recipient.two_factor:
            settings.protectionLevel = ProtectionLevel.Email
        else:
            settings.protectionLevel = ProtectionLevel.Public
    else:
        invitee = recipient.collaborator
    settings.invitee = invitee
    param.shares.append(settings)


def find_recipients_to_remove(param, path, current_accounts, accounts):
    current_accounts = obtain_current_accounts(param)
    accounts_to_keep, accounts_to_remove = [], []
    if current_accounts:
        for idx, current_account in enumerate(current_accounts):
            if current_account not in accounts:
                accounts_to_keep.append(param.shares[idx])
            else:
                logger.debug('Found recipient to remove: %s', str(current_account))
                accounts_to_remove.append(current_account)
        if not accounts_to_remove:
            logger.debug('Share recipients not found: %s', [str(member) for member in accounts])
        else:
            logger.debug('Removing share recipients: %s', [str(account) for account in accounts_to_remove])
    else:
        logger.debug('Share has no recipients. %s', path.relative)
    return accounts_to_keep, accounts_to_remove


def find_recipients_to_add(path, param, current_accounts, valid_recipients):
    current_accounts = obtain_current_accounts(param)
    accounts_to_add = []
    if valid_recipients:
        for recipient in valid_recipients:
            if recipient.account not in current_accounts:
                logger.debug('New share recipient: %s', str(recipient.account))
                accounts_to_add.append(recipient)
            else:
                logger.debug('Share recipient already exists: %s', str(recipient.account))
        if accounts_to_add:
            logger.debug('Adding share recipients: %s', [str(recipient.account) for recipient in accounts_to_add])
        else:
            logger.warning('Could not find new share recipients: %s', path.relative)
        return accounts_to_add
    logger.warning('Could not find valid share recipients: %s', path.relative)
    return accounts_to_add


class SearchMember(PortalCommand):

    def __init__(self, function, receiver, account, cloud_folder_uid):
        super().__init__(function, receiver)
        self.account = account
        self.cloud_folder_uid = cloud_folder_uid

    def _before_command(self):
        logger.info('Searching member: %s', self.account.upn)

    def get_parameter(self):
        param = Object()
        if self.account.account_type == PortalAccountType.User:
            param.searchType = SearchType.Users
        elif self.account.account_type == PortalAccountType.Group:
            param.searchType = SearchType.Groups
        else:
            raise ValueError(f'Invalid account type: {self.account.account_type}')
        param.searchTerm = self.account.name
        param.resourceUid = self.cloud_folder_uid
        param.countLimit = 1
        return param

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_response(self, r):
        if not r.objects:
            logger.warning('Could not find results that match your search criteria. %s', {'name': self.account.name})
        elif len(r.objects) > 1:
            logger.warning('Search returned multiple results. Skipping...')
        else:
            collaborator = r.objects.pop()
            if self.account.is_local:
                if self.account.account_type == PortalAccountType.User and collaborator.type == CollaboratorType.LU:
                    logger.debug('Local User: %s', self.account.name)
                    return collaborator
                if self.account.account_type == PortalAccountType.Group and collaborator.type == CollaboratorType.LG:
                    logger.debug('Local Group: %s', self.account.name)
                    return collaborator
                logger.warning('Expected to find local %s but found domain %s', self.account.account_type, self.account.account_type)
            else:
                if self.account.account_type == PortalAccountType.User and collaborator.type == CollaboratorType.DU:
                    logger.debug('Domain User: %s', f'{self.account.name}@{self.account.directory}')
                    return collaborator
                if self.account.account_type == PortalAccountType.Group and collaborator.type == CollaboratorType.DG:
                    logger.debug('Domain Group: %s', f'{self.account.name}@{self.account.directory}')
                    return collaborator
                logger.warning('Expected to find domain %s but found local %s', self.account.account_type, self.account.account_type)
        return None


def valid_recipient(recipient):
    is_valid = True
    if not recipient.account:
        logger.warning('No account information found. Skipping. %s', {'account': recipient.account})
        is_valid = False
    if not isinstance(recipient.account, (str, UserAccount, GroupAccount)):
        logger.warning('Invalid recipient type. Skipping. %s', {'type': type(recipient.account)})
        is_valid = False
    if recipient.access not in [v for k, v in FileAccessMode.__dict__.items() if not k.startswith('_')]:
        logger.warning('Invalid file access mode. Skipping. %s', {'account': str(recipient.account), 'access': recipient.access})
        is_valid = False
    if recipient.type == CollaboratorType.EXT and not isinstance(recipient.account, str):
        logger.warning('Invalid external recipient type. Skipping. %s', {'expected': 'str', 'actual': type(recipient.account)})
        is_valid = False
    if recipient.type in [CollaboratorType.LU, CollaboratorType.LG] and not recipient.account.is_local:
        logger.warning('Expected local account. Received a domain account. Skipping. %s', {'account': str(recipient.account)})
        is_valid = False
    if recipient.type in [CollaboratorType.DU, CollaboratorType.DG] and recipient.account.is_local:
        logger.warning('Expected domain account. Received a local account. Skipping. %s', {'account': str(recipient.account)})
        is_valid = False
    return is_valid


def obtain_current_accounts(param):
    current_accounts = []
    for collaborator in param.shares:
        if collaborator.invitee.type == CollaboratorType.EXT:
            current_accounts.append(collaborator.invitee.email)
        else:
            current_accounts.append(PortalAccount.from_collaborator(collaborator.invitee))
    return current_accounts


class Open(PortalCommand):
    """Open file"""

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = path

    def get_parameter(self):
        return self.path.reference

    def _before_command(self):
        logger.info('Getting handle: %s', self.path.relative)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class Download(PortalCommand):

    def __init__(self, function, receiver, path, destination):
        super().__init__(function, receiver)
        self.path = path
        self.destination = destination

    def get_parameter(self):
        return commonfs.determine_directory_and_filename(self.path.reference, destination=self.destination)

    def _before_command(self):
        logger.info('Downloading: %s', self.path.relative)

    def _execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            with Open(self._function, self._receiver, self.path) as handle:
                return synfs.write(directory, name, handle)

    async def _a_execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            async with Open(self._function, self._receiver, self.path) as handle:
                return await asynfs.write(directory, name, handle)


class OpenMany(PortalCommand):

    def __init__(self, function, receiver, directory, *objects):
        super().__init__(function, receiver)
        self.directory = directory
        self.objects = objects

    def _before_command(self):
        logger.info('Getting handle: %s', [self.directory.join(o).relative for o in self.objects])

    def get_parameter(self):
        param = Object()
        param.paths = ['/'.join([self.directory.absolute, filename]) for filename in self.objects]
        param.snapshot = None
        param.password = None
        param.portalName = None
        param.showDeleted = False
        return common.encode_request_parameter(param)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter(), self.directory)

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter(), self.directory)


class DownloadMany(PortalCommand):

    def __init__(self, function, receiver, target, objects, destination):
        super().__init__(function, receiver)
        self.target = target
        self.objects = objects
        self.destination = destination

    def get_parameter(self):
        return commonfs.determine_directory_and_filename(self.target.reference, self.objects, destination=self.destination, archive=True)

    def _before_command(self):
        for o in self.objects:
            logger.info('Downloading: %s', self.target.join(o).relative)

    def _execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            with OpenMany(self._function, self._receiver, self.target, *self.objects) as handle:
                return synfs.write(directory, name, handle)

    async def _a_execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            async with OpenMany(self._function, self._receiver, self.target, *self.objects) as handle:
                return await asynfs.write(directory, name, handle)


class ListDirectory(PortalCommand):
    """List"""

    def __init__(self, function, receiver, path, depth, include_deleted, search_criteria, limit):
        super().__init__(function, receiver)
        self.path = path
        self.depth = depth
        self.include_deleted = include_deleted
        self.search_criteria = search_criteria
        self.limit = limit

    def get_parameter(self):
        depth = self.depth if self.depth is not None else 1
        builder = FetchResourcesParamBuilder().root(self.path.absolute_encode).depth(depth)
        if self.include_deleted:
            builder.include_deleted()
        if self.search_criteria:
            builder.searchCriteria(self.search_criteria)
        if self.limit:
            builder.limit(self.limit)
        return builder.build()

    def _before_command(self):
        logger.info('Listing directory: %s', self.path.relative)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class ResourceIterator(ListDirectory):

    def __init__(self, function, receiver, path, depth, include_deleted, search_criteria, limit):
        super().__init__(function, receiver, path, depth, include_deleted, search_criteria, limit)

    def execute(self):
        try:
            return super().execute()
        except FetchResourcesError as e:
            self._handle_exception(e)

    def _fetch_resources(self):
        return self._function(self._receiver, '', self.get_parameter(), 'fetchResources', callback_response=FetchResourcesResponse)

    def _execute(self):
        with self.trace_execution():
            return self._fetch_resources()

    def _a_execute(self):
        return super()._a_execute()

    def _handle_exception(self, e):
        return super()._handle_exception(e)


class GetMetadata(ListDirectory):

    def __init__(self, function, receiver, path, suppress_error=False):
        super().__init__(function, receiver, path, 0, False, None, None)
        self.suppress_error = suppress_error

    def _before_command(self):
        logger.info('Getting metadata: %s', self.path.relative)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_response(self, r):
        if r.root is None:
            if not self.suppress_error:
                raise ResourceNotFoundError(self.path.relative)
            return False, None
        return True, r.root


class GetPermalink(GetMetadata):

    def _handle_response(self, r):
        _, metadata = r
        return metadata.permalink


class RecursiveIterator:

    def __init__(self, function, receiver, path, include_deleted):
        self._function = function
        self._receiver = receiver
        self.path = path
        self.include_deleted = include_deleted
        self.tree = [CorePath.instance(path.scope, path.relative)]

    def _generator(self):
        while len(self.tree) > 0:
            yield self.tree.pop(0)

    def _before_generate(self):
        EnsureDirectory(self._function, self._receiver, CorePath.instance(self.path.scope, self.path.relative))
        logger.info('Traversing: %s', self.path.relative)

    def generate(self):
        self._before_generate()
        for path in self._generator():
            for o in ResourceIterator(self._function, self._receiver, path, None, self.include_deleted, None, None).execute():
                yield self._process_object(o)

    async def a_generate(self):
        for path in self._generator():
            async for o in ResourceIterator(self._function, self._receiver, path, None, self.include_deleted, None, None).execute():
                yield self._process_object(o)

    def _process_object(self, o):
        if o.isFolder:
            self.tree.append(CorePath.instance(self.path.scope, o))
        return o


class ListVersions(PortalCommand):

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = path

    def _before_command(self):
        logger.info('Getting versions: %s', self.path.relative)

    def get_parameter(self):
        return self.path.absolute

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class CreateDirectory(PortalCommand):
    """Create Directory"""

    def __init__(self, function, receiver, path, parents=False):
        super().__init__(function, receiver)
        self.path = path
        self.parents = parents

    def get_parameter(self):
        param = Object()
        param.name = self.path.name
        param.parentPath = self.path.parent.absolute_encode
        return param

    def _before_command(self):
        logger.info('Creating directory: %s', self.path.relative)

    def _parents_generator(self):
        if self.parents:
            parts = self.path.parts
            for i in range(1, len(parts)):
                yield CorePath.instance(self.path.scope, '/'.join(parts[:i]))
        else:
            yield self.path

    def _execute(self):
        if self.parents:
            for path in self._parents_generator():
                try:
                    CreateDirectory(self._function, self._receiver, path).execute()
                except FileExistsError:
                    pass
        return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        if self.parents:
            for path in self._parents_generator():
                try:
                    await CreateDirectory(self._function, self._receiver, path).a_execute()
                except FileExistsError:
                    pass
        return await self._function(self._receiver, self.get_parameter())

    def _handle_response(self, r):
        path = self.path.relative
        if r is None or r == 'Ok':
            return path
        if r == ResourceError.FileWithTheSameNameExist:
            raise FileExistsError(path)
        if r == ResourceError.DestinationNotExists:
            raise PathValidationError(path)
        if r == ResourceError.ReservedName:
            raise ReservedNameError(path)
        if r == ResourceError.InvalidName:
            raise NameSyntaxError(path)
        if r == ResourceError.PermissionDenied:
            raise PermissionDenied(path)


class GetShareMetadata(PortalCommand):
    
    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = path

    def _before_command(self):
        logger.info('Share metadata: %s', self.path.relative)

    def get_parameter(self):
        return self.path.absolute_encode

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_exception(self, e):
        # Catch internal server error: e.error.response.error.msg: 'Resource does not exist'
        return super()._handle_exception(e)


class Link(PortalCommand):

    def __init__(self, function, receiver, path, access, expire_in):
        super().__init__(function, receiver)
        self.path = path
        self.access = access
        self.expire_in = expire_in

    def _before_command(self):
        logger.info('Creating Public Link: %s', self.path.relative)

    def get_parameter(self):
        access = {'RO': 'ReadOnly', 'RW': 'ReadWrite', 'PO': 'PreviewOnly'}.get(self.access)
        expire_on = DateTimeUtils.get_expiration_date(self.expire_in).strftime('%Y-%m-%d')
        param = CreateShareParam.instance(path=self.path.absolute_encode, access=access, expire_on=expire_on)
        return param

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_response(self, r):
        return r.publicLink


class FilterShareMembers(PortalCommand):

    def __init__(self, function, receiver, members, cloud_folder_uid):
        super().__init__(function, receiver)
        self.members = members
        self.cloud_folder_uid = cloud_folder_uid

    def _execute(self):
        members = []
        for member in filter(valid_recipient, self.members):
            if not member.type == CollaboratorType.EXT:
                collaborator = SearchMember(self._function, self._receiver, member.account, self.cloud_folder_uid).execute()
                if collaborator:
                    member.collaborator = collaborator
                    members.append(member)
            else:
                members.append(member)
        return members

    async def _a_execute(self):
        pass


class Share(PortalCommand):

    def __init__(self, function, receiver, path, members, as_project, allow_reshare, allow_sync):
        super().__init__(function, receiver)
        self.path = path
        self.members = members
        self.as_project = as_project
        self.allow_reshare = allow_reshare
        self.allow_sync = allow_sync

    def _before_command(self):
        logger.info('Sharing: %s', self.path.relative)

    def get_parameter(self):
        return create_share_parameter(self.path, self.as_project, self.allow_reshare, self.allow_sync)

    def _execute(self):
        if self.members:
            param = self.get_parameter()
            for recipient in self.members:
                add_share_recipient(param, recipient)
            with self.trace_execution():
                self._function(self._receiver, param)
            return self.members

    async def _a_execute(self):
        pass


class AddMembers(PortalCommand):

    def __init__(self, function, receiver, path, metadata, members):
        super().__init__(function, receiver)
        self.path = path
        self.metadata = metadata
        self.members = members
        self._new_members = None

    def get_parameter(self):
        return create_share_parameter(self.path, self.metadata.teamProject, self.metadata.allowReshare, self.metadata.shouldSync, self.metadata.shares)

    def _before_command(self):
        logger.info('Granting access for: (%s) to: %s',
                    ', '.join([m.account if isinstance(m.account, str) else m.account.upn for m in self._new_members]),
                    self.path.relative)

    def _execute(self):
        current_accounts = obtain_current_accounts(self.metadata)
        param = self.get_parameter()
        self._new_members = find_recipients_to_add(self.path, self.metadata, current_accounts, self.members)
        if self._new_members:
            for recipient in self._new_members:
                add_share_recipient(param, recipient)
            with self.trace_execution():
                self._function(self._receiver, param)
        return self.members

    async def _a_execute(self):
        pass


class RemoveMembers(PortalCommand):

    def __init__(self, function, receiver, path, metadata, members):
        super().__init__(function, receiver)
        self.path = path
        self.metadata = metadata
        self.members = members
        self._to_remove = None

    def _before_command(self):
        logger.info('Revoking access for: (%s) from: %s', ','.join(m.upn for m in self._to_remove), self.path.relative)

    def get_parameter(self):
        return create_share_parameter(self.path, self.metadata.teamProject, self.metadata.allowReshare, self.metadata.shouldSync, self.members)

    def _execute(self):
        current_accounts = obtain_current_accounts(self.metadata)
        self.members, self._to_remove = find_recipients_to_remove(self.metadata, self.path, current_accounts, self.members)
        if self._to_remove:
            param = self.get_parameter()
            with self.trace_execution():
                self._function(self._receiver, param)
        return self._to_remove

    async def _a_execute(self):
        pass


class UnShare(PortalCommand):

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = path

    def get_parameter(self):
        return create_share_parameter(self.path, True, True, True)

    def _before_command(self):
        logger.info('Revoking Share: %s', self.path.relative)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class BackgroundPortalCommand(PortalCommand):

    def __init__(self, function, receiver, block):
        super().__init__(function, receiver)
        self.block = block
        self.background = True

    @abstractmethod
    def _action_message(self):
        raise NotImplementedError("Subclass must implement the '_action_message' method")

    def _background_function(self):
        if asyncio.iscoroutinefunction(self._function):
            async def wrapper(param):
                task_reference = await self._function(self._receiver, param)
                if self.block:
                    return await self._receiver.tasks.wait(task_reference)
                return self._receiver.tasks.awaitable_task(task_reference)
        else:
            def wrapper(param):
                task_reference = self._function(self._receiver, param)
                if self.block:
                    return self._receiver.tasks.wait(task_reference)
                return self._receiver.tasks.awaitable_task(task_reference)
        return wrapper

    def _execute(self):
        with self.trace_execution():
            function = self._background_function()
            return function(self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            function = self._background_function()
            return await function(self.get_parameter())


class Rename(BackgroundPortalCommand):

    def __init__(self, function, receiver, path, new_name, block):
        super().__init__(function, receiver, block)
        self.path = path
        self.new_name = new_name

    def _action_message(self):
        return 'Renaming'

    def get_parameter(self):
        param = ActionResourcesParam.instance()
        param.add(SrcDstParam.instance(src=self.path.absolute_encode, dest=self.path.parent.join(self.new_name).absolute_encode))
        return param

    def _before_command(self):
        logger.info('%s: %s, to: %s', self._action_message(), self.path.relative, self.path.parent.join(self.new_name).relative)


class MultiResourceCommand(BackgroundPortalCommand):

    def __init__(self, function, receiver, block, *paths):
        super().__init__(function, receiver, block)
        self.paths = paths

    def get_parameter(self):
        param = ActionResourcesParam.instance()
        paths = [paths] if not isinstance(self.paths, tuple) else self.paths
        for path in paths:
            param.add(SrcDstParam.instance(src=path.absolute_encode))
        return param

    def _before_command(self):
        for path in self.paths:
            logger.info('%s: %s', self._action_message(), path.relative)


class Delete(MultiResourceCommand):

    def __init__(self, function, receiver, block, *paths):
        super().__init__(function, receiver, block, *paths)

    def _action_message(self):
        return 'Deleting'


class Recover(MultiResourceCommand):

    def __init__(self, function, receiver, block, *paths):
        super().__init__(function, receiver, block, *paths)

    def _action_message(self):
        return 'Recovering'


class ResolverCommand(BackgroundPortalCommand):

    def __init__(self, function, receiver, block, *paths, destination=None, resolver=None, cursor=None):
        super().__init__(function, receiver, block)
        self.paths = paths
        self.destination = destination
        self.resolver = resolver
        self.cursor = cursor

    def get_parameter(self):

        param = ActionResourcesParam.instance()
        if self.cursor:
            param.startFrom = self.cursor

        if self.cursor and self.resolver:
            if self.resolver.all:
                param.startFrom.fileMoveConflictResolutaion = [self.resolver.build()]
            else:
                param.startFrom.skipHandler = self.resolver.handler

        for path in self.paths:
            src, dest = path, self.destination
            if isinstance(path, tuple):
                src, dest = path
            else:
                if not dest.reference.name:
                    raise ValueError(f'Error: No destination specified for: {src}')
                dest = dest.join(src.name)
            param.add(SrcDstParam.instance(src=src.absolute_encode, dest=dest.absolute_encode))

        return param

    def _before_command(self):
        for path in self.paths:
            src, dest = path, self.destination
            if isinstance(path, tuple):
                src, dest = path
            logger.info('%s: %s to: %s', self._action_message(), src.relative, dest.relative)

    @abstractmethod
    def _action_message(self):
        raise NotImplementedError("Subclass must implement the '_action_message' method")         

    def execute(self):
        try:
            super().execute()
        except FileConflict as e:
            if self.resolver:
                return self._try_with_resolver(e.cursor)

    async def a_execute(self):
        try:
            await super().a_execute()
        except FileConflict as e:
            if self.resolver:
                return await self._a_try_with_resolver(e.cursor)

    def _handle_response(self, r):
        if not self.block:
            return r

        if r.error_type == 'Conflict':
            raise FileConflict(r.cursor)


class Copy(ResolverCommand):

    def __init__(self, function, receiver, block, *paths, destination=None, resolver=None, cursor=None):
        super().__init__(function, receiver, block, *paths, destination=destination, resolver=resolver, cursor=cursor)

    def _action_message(self):
        return 'Copying'

    def _try_with_resolver(self, cursor):
        return Copy(self._function, self._receiver, self.block, *self.paths, destination=self.destination, resolver=self.resolver, cursor=cursor).execute()

    async def _a_try_with_resolver(self, cursor):
        return await Copy(self._function, self._receiver, self.block, *self.paths, destination=self.destination, resolver=self.resolver, cursor=cursor).a_execute()


class Move(ResolverCommand):

    def __init__(self, function, receiver, block, *paths, destination=None, resolver=None, cursor=None):
        super().__init__(function, receiver, block, *paths, destination=destination, resolver=resolver, cursor=cursor)

    def _action_message(self):
        return 'Moving'

    def _try_with_resolver(self, cursor):
        return Move(self._function, self._receiver, self.block, *self.paths, destination=self.destination, resolver=self.resolver, cursor=cursor).execute()

    async def _a_try_with_resolver(self, cursor):
        return await Move(self._function, self._receiver, self.block, *self.paths, destination=self.destination, resolver=self.resolver, cursor=cursor).a_execute()
