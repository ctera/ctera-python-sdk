# pylint: disable=too-many-lines

import re
import logging
import asyncio
from abc import abstractmethod
from contextlib import contextmanager
from ...common import Object, DateTimeUtils
from ...core.enum import ProtectionLevel, CollaboratorType, SearchType, PortalAccountType, FileAccessMode, \
    UploadError, ResourceScope, ResourceError
from ...core.types import PortalAccount, UserAccount, GroupAccount, Collaborator
from ... import exceptions
from ...lib.storage import synfs, asynfs, commonfs
from .types import SrcDstParam, CreateShareParam, ActionResourcesParam, FetchResourcesError, \
    FetchResourcesParamBuilder, FetchResourcesResponse, PortalResource, PreviousVersion, automatic_resolution
from ..common import encode_request_parameter, encode_stream
from ..actions import PortalCommand


logger = logging.getLogger('cterasdk.core')


def split_file_directory(listdir, receiver, destination):
    """
    Split a path into its parent directory and final component.

    :returns:
        tuple[str, str]: A ``(parent_directory, name)`` tuple when:

        * The path refers to an existing file
        * The path refers to an existing directory
        * The parent directory of the path exists

    :raises cterasdk.exceptions.io.core.GetMetadataError: If neither the path nor its parent directory exist.
    """
    is_dir, resource = EnsureDirectory(listdir, receiver, destination, True).execute()
    if not is_dir:
        is_dir, resource = EnsureDirectory(listdir, receiver, destination.parent).execute()
        return resource, destination.parent, destination.name
    return resource, destination, None


async def a_split_file_directory(listdir, receiver, destination):
    """
    Split a path into its parent directory and final component.

    :returns:
        tuple[str, str]: A ``(parent_directory, name)`` tuple when:

        * The path refers to an existing file
        * The path refers to an existing directory
        * The parent directory of the path exists

    :raises cterasdk.exceptions.io.core.GetMetadataError: If neither the path nor its parent directory exist.
    """
    is_dir, resource = await EnsureDirectory(listdir, receiver, destination, True).a_execute()
    if not is_dir:
        is_dir, resource = await EnsureDirectory(listdir, receiver, destination.parent).a_execute()
        return resource, destination.parent, destination.name
    return resource, destination, None


class PathResolver:

    def __init__(self, listdir, receiver, destination, default):
        self._listdir = listdir
        self._receiver = receiver
        self._destination = destination
        self._default = default

    async def a_resolve(self):
        resource, parent, name = await a_split_file_directory(self._listdir, self._receiver, self._destination)
        return resource, self._resolve(parent, name)

    def resolve(self):
        resource, parent, name = split_file_directory(self._listdir, self._receiver, self._destination)
        return resource, self._resolve(parent, name)

    def _resolve(self, parent, name):
        if name is not None:
            return parent.join(name)
        if self._default is not None:
            return parent.join(self._default)
        return self._destination


def destination_prerequisite_conditions(destination):
    if any(c in destination.name for c in ['\\', '/', ':', '?', '&', '<', '>', '"', '|']):
        raise exceptions.io.core.FilenameError(destination.relative)


class EnsureDirectory(PortalCommand):

    def __init__(self, function, receiver, path, suppress_error=False):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)
        self.suppress_error = suppress_error

    def _execute(self):
        return GetMetadata(self._function, self._receiver, self.path, self.suppress_error).execute()

    async def _a_execute(self):
        return await GetMetadata(self._function, self._receiver, self.path, self.suppress_error).a_execute()

    def _handle_response(self, r):
        exists, resource = r
        if (not exists or not resource.isFolder) and not self.suppress_error:
            raise exceptions.io.core.NotADirectoryException(self.path.relative)
        return resource.isFolder if exists else False, resource


def ensure_writeable(resource, directory):
    if resource.scope == ResourceScope.Root:
        raise exceptions.io.core.ROFSError('/')
    if resource.scope not in [ResourceScope.Personal, ResourceScope.Project, ResourceScope.InsideCloudFolder]:
        raise exceptions.io.core.ROFSError(directory.relative)
    if resource.permission != FileAccessMode.RW:
        raise exceptions.io.core.PrivilegeError(directory.relative)


class Upload(PortalCommand):

    def __init__(self, function, receiver, listdir, destination, fd, name, size):
        super().__init__(function, receiver)
        self.destination = automatic_resolution(destination, receiver.context)
        self._resolver = PathResolver(listdir, receiver, self.destination, name)
        self.size = size
        self.fd = fd
        self._resource = None

    def get_parameter(self):
        fd, size = encode_stream(self.fd, self.size)
        param = dict(
            name=self.destination.name,
            Filename=self.destination.name,
            fullpath=self._receiver.io.builder(self.destination.relative_encode),
            fileSize=size,
            file=fd
        )
        return param

    def _before_command(self):
        destination_prerequisite_conditions(self.destination)
        ensure_writeable(self._resource, self.destination.parent)
        logger.info('Uploading: %s', self.destination)

    def _execute(self):
        self._resource, self.destination = self._resolver.resolve()
        with self.trace_execution():
            return self._function(self._receiver, str(self._resource.cloudFolderInfo.uid), self.get_parameter())

    async def _a_execute(self):
        self._resource, self.destination = await self._resolver.a_resolve()
        with self.trace_execution():
            return await self._function(self._receiver, str(self._resource.cloudFolderInfo.uid), self.get_parameter())

    def _handle_response(self, r):
        path = self.destination.relative
        if r.rc:
            error = exceptions.io.core.UploadError(r.msg, path)
            logger.error('Upload failed: %s', path)
            if r.msg in [UploadError.UserQuotaViolation, UploadError.PortalQuotaViolation, UploadError.FolderQuotaViolation]:
                raise error from exceptions.io.core.QuotaError(path)
            if r.msg == UploadError.RejectedByPolicy:
                raise error from exceptions.io.core.FileRejectedError(path)
            if r.msg == UploadError.WindowsACL:
                raise error from exceptions.io.core.NTACLError(path)
            if r.msg.startswith(UploadError.NoStorageBucket):
                raise error from exceptions.io.core.StorageBackendError(path)
            raise error
        if not r.rc and r.msg == 'OK':
            logger.info('Upload success. Saved to: %s', path)
        return path


def _is_sharing_on_user_behalf(path):
    return re.match(r'^Users/[^/]+(?=/)', path.relative) is not None


def _is_subfolder(path):
    depth = len(path.reference.parts)
    sharing_on_user_behalf = _is_sharing_on_user_behalf(path)
    return (sharing_on_user_behalf and depth > 3) or (not sharing_on_user_behalf and depth > 1)


def create_collaboration_parameter(path, as_project, allow_reshare, allow_sync):
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
    return param


def create_collaborator(member):
    settings = Object()
    settings._classname = 'ShareConfig'  # pylint: disable=protected-access
    settings.accessMode = member.access
    if not member.access == FileAccessMode.NA:
        settings.expiration = member.expiration_date
    invitee = None
    if member.type == CollaboratorType.EXT:
        invitee = Object()
        invitee._classname = 'Collaborator'  # pylint: disable=protected-access
        invitee.type = member.type
        invitee.email = member.account
        if member.two_factor:
            settings.protectionLevel = ProtectionLevel.Email
        else:
            settings.protectionLevel = ProtectionLevel.Public
    else:
        invitee = member.collaborator
    settings.invitee = invitee
    return settings


def extend_collaborators(collaborators, valid_members):
    current_accounts = obtain_current_accounts(collaborators)
    accounts_to_add = []
    if valid_members:
        for member in valid_members:
            if member.account not in current_accounts:
                logger.debug('New member: %s', str(member.account))
                accounts_to_add.append(member)
            else:
                logger.debug('Member exists: %s', str(member.account))
        if accounts_to_add:
            logger.debug('Adding member: %s', [str(member.account) for member in accounts_to_add])
        else:
            logger.warning('No new members found.')
        collaborators.extend([create_collaborator(account) for account in accounts_to_add])
        return collaborators
    logger.warning('No valid members found.')
    return collaborators


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


def obtain_current_accounts(collaborators):
    current_accounts = []
    for collaborator in collaborators:
        if collaborator.invitee.type == CollaboratorType.EXT:
            current_accounts.append(collaborator.invitee.email)
        else:
            current_accounts.append(PortalAccount.from_collaborator(collaborator.invitee))
    return current_accounts


class Open(PortalCommand):
    """Open file"""

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)

    def get_parameter(self):
        return self.path.reference

    def _before_command(self):
        logger.info('Getting handle: %s', self.path)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_exception(self, e):
        path = self.path.relative
        error = exceptions.io.edge.OpenError(path)
        if isinstance(e, exceptions.transport.NotFound):
            raise error from exceptions.io.core.FileNotFoundException(path)
        raise error


class Download(PortalCommand):

    def __init__(self, function, receiver, path, destination):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)
        self.destination = destination

    def get_parameter(self):
        return commonfs.determine_directory_and_filename(self.path.reference, destination=self.destination)

    def _before_command(self):
        logger.info('Downloading: %s', self.path)

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

    def __init__(self, function, receiver, resource, directory, *objects):
        super().__init__(function, receiver)
        self.uid = str(resource.cloudFolderInfo.uid)
        self.directory = automatic_resolution(directory, receiver.context)
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
        return encode_request_parameter(param)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.uid, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.uid, self.get_parameter())


class DownloadMany(PortalCommand):

    def __init__(self, function, receiver, resource, directory, objects, destination):
        super().__init__(function, receiver)
        self.resource = resource
        self.directory = automatic_resolution(directory, receiver.context)
        self.objects = objects
        self.destination = destination

    def get_parameter(self):
        return commonfs.determine_directory_and_filename(self.directory.reference, self.objects, destination=self.destination, archive=True)

    def _before_command(self):
        for o in self.objects:
            logger.info('Downloading: %s', self.directory.join(o).relative)

    def _execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            with OpenMany(self._function, self._receiver, self.resource, self.directory, *self.objects) as handle:
                return synfs.write(directory, name, handle)

    async def _a_execute(self):
        directory, name = self.get_parameter()
        with self.trace_execution():
            async with OpenMany(self._function, self._receiver, self.resource, self.directory, *self.objects) as handle:
                return await asynfs.write(directory, name, handle)


class ListDirectory(PortalCommand):
    """List"""

    def __init__(self, function, receiver, path, depth, include_deleted, search_criteria, limit):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)
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
        logger.info('Listing directory: %s', self.path)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())


class ResourceIterator(ListDirectory):

    def execute(self):
        try:
            for o in super().execute():
                yield PortalResource.from_server_object(o)
        except FetchResourcesError as e:
            self._fetch_resources_error(e)

    async def a_execute(self):
        try:
            async for o in self._execute():
                yield PortalResource.from_server_object(o)
        except FetchResourcesError as e:
            self._fetch_resources_error(e)

    def _fetch_resources(self):
        return self._function(self._receiver, '', self.get_parameter(), 'fetchResources', callback_response=FetchResourcesResponse)

    def _execute(self):
        with self.trace_execution():
            return self._fetch_resources()

    def _fetch_resources_error(self, e):
        error = exceptions.io.core.ListDirectoryError(self.path.relative)
        if e.error == ResourceError.DestinationNotExists:
            raise error from exceptions.io.core.FolderNotFoundError(self.path.relative)
        raise error from e


class GetMetadata(ListDirectory):

    def __init__(self, function, receiver, path, suppress_error=False):
        super().__init__(function, receiver, path, 0, False, None, None)
        self.suppress_error = suppress_error

    def _before_command(self):
        logger.info('Getting metadata: %s', self.path)

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_response(self, r):
        if r.root is None:
            if not self.suppress_error:
                cause = exceptions.io.core.ObjectNotFoundError(self.path.relative)
                raise exceptions.io.core.GetMetadataError(self.path.relative) from cause
            return False, None
        return True, r.root


class GetProperties(GetMetadata):

    def _handle_response(self, r):
        _, metadata = super()._handle_response(r)
        return PortalResource.from_server_object(metadata)


class GetPermalink(GetMetadata):

    def _handle_response(self, r):
        _, metadata = super()._handle_response(r)
        return metadata.permalink


class RecursiveIterator:

    def __init__(self, function, receiver, path, include_deleted):
        self._function = function
        self._receiver = receiver
        self.path = path
        self.include_deleted = include_deleted
        self.tree = [path]

    def _generator(self):
        logger.info('Traversing: %s', self.path or '.')
        while len(self.tree) > 0:
            yield self.tree.pop(0)

    def generate(self):
        for path in self._generator():
            try:
                print('Enumerating: ', path or '.')
                for o in ResourceIterator(self._function, self._receiver, path, None, self.include_deleted, None, None).execute():
                    yield self._process_object(o)
            except exceptions.io.core.ListDirectoryError as e:
                RecursiveIterator._suppress_error(e)

    async def a_generate(self):
        for path in self._generator():
            try:
                async for o in ResourceIterator(self._function, self._receiver, path, None, self.include_deleted, None, None).a_execute():
                    yield self._process_object(o)
            except exceptions.io.core.ListDirectoryError as e:
                RecursiveIterator._suppress_error(e)

    def _process_object(self, o):
        if o.is_dir:
            self.tree.append(o.path.relative)
        return o

    @staticmethod
    def _suppress_error(e):
        if not isinstance(e.__cause__, exceptions.io.core.FolderNotFoundError):
            raise e
        logger.warning("Could not list directory contents: %s. No such directory.", e.path)


class ListVersions(PortalCommand):

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)

    def _before_command(self):
        logger.info('Listing versions: %s', self.path)

    def get_parameter(self):
        return self.path.absolute

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_response(self, r):
        return [PreviousVersion.from_server_object(v) for v in r]

    def _handle_exception(self, e):
        raise exceptions.io.core.GetVersionsError(self.path.relative) from e


class CreateDirectory(PortalCommand):
    """Create Directory"""

    def __init__(self, function, receiver, path, parents=False):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)
        self.parents = parents

    def get_parameter(self):
        param = Object()
        param.name = self.path.name
        param.parentPath = self.path.parent.absolute_encode
        return param

    def _before_command(self):
        logger.info('Creating directory: %s', self.path)

    def _parents_generator(self):
        if self.parents:
            parts = self.path.parts
            for i in range(1, len(parts)):
                yield automatic_resolution('/'.join(parts[:i]), self._receiver.context)
        else:
            yield self.path

    def _execute(self):
        if self.parents:
            for path in self._parents_generator():
                try:
                    CreateDirectory(self._function, self._receiver, path).execute()
                except exceptions.io.core.CreateDirectoryError as e:
                    CreateDirectory._suppress_file_conflict_error(e)
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        if self.parents:
            for path in self._parents_generator():
                try:
                    await CreateDirectory(self._function, self._receiver, path).a_execute()
                except exceptions.io.core.CreateDirectoryError as e:
                    CreateDirectory._suppress_file_conflict_error(e)
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    @staticmethod
    def _suppress_file_conflict_error(e):
        if not isinstance(e.__cause__, exceptions.io.core.FileConflictError):
            raise e

    def _handle_response(self, r):
        path = self.path.relative
        if r is None or r == 'Ok':
            return path

        error, cause = exceptions.io.core.CreateDirectoryError(path), None
        if r == ResourceError.FileWithTheSameNameExist:
            cause = exceptions.io.core.FileConflictError(path)
        if r == ResourceError.DestinationNotExists:
            cause = exceptions.io.core.FolderNotFoundError(self.path.parent.relative)
        if r == ResourceError.ReservedName:
            cause = exceptions.io.core.ReservedNameError(path)
        if r == ResourceError.InvalidName:
            cause = exceptions.io.core.FilenameError(path)
        if r == ResourceError.PermissionDenied:
            cause = exceptions.io.core.ReservedNameError(path)

        raise error from cause


class GetShareMetadata(PortalCommand):

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)

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
        path = self.path.relative
        error = exceptions.io.core.GetShareMetadataError(path)
        if e.error.response.error.msg == 'Resource does not exist':
            raise error from exceptions.io.core.ObjectNotFoundError(path)
        raise exceptions.io.core.GetShareMetadataError(path) from e


class Link(PortalCommand):

    def __init__(self, function, receiver, path, access, expire_in):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)
        self.access = access
        self.expire_in = expire_in

    def _before_command(self):
        logger.info('Creating Public Link: %s', self.path)

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

    def _handle_exception(self, e):
        path = self.path.relative
        error = exceptions.io.core.CreateLinkError(path)
        if e.error.response.error.msg == 'Resource does not exist':
            raise error from exceptions.io.core.ObjectNotFoundError(path)
        raise error from e


class FilterShareMembers(PortalCommand):

    def __init__(self, function, receiver, members, cloud_folder_uid):
        super().__init__(function, receiver)
        self.members = members
        self.cloud_folder_uid = cloud_folder_uid

    @staticmethod
    def _valid_recipient(recipient):
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

    @contextmanager
    def _enumerate_members(self, collaborators):
        internals = []
        for member in filter(FilterShareMembers._valid_recipient, self.members):
            if member.type == CollaboratorType.EXT:
                collaborators.append(member)
            else:
                internals.append(member)
        yield internals
        collaborators.extend([member for member in internals if member.collaborator is not None])

    def _execute(self):
        collaborators = []
        with self._enumerate_members(collaborators) as members:
            for member in members:
                member.collaborator = SearchMember(self._function, self._receiver, member.account, self.cloud_folder_uid).execute()
        return collaborators

    async def _a_execute(self):
        collaborators = []
        with self._enumerate_members(collaborators) as members:
            for member in members:
                member.collaborator = await SearchMember(self._function,
                                                         self._receiver, member.account, self.cloud_folder_uid).a_execute()
        return collaborators


class Share(PortalCommand):

    def __init__(self, function, receiver, path, members, as_project, allow_reshare, allow_sync):
        super().__init__(function, receiver)
        self.path = automatic_resolution(path, receiver.context)
        self.members = members
        self.as_project = as_project
        self.allow_reshare = allow_reshare
        self.allow_sync = allow_sync

    def _before_command(self):
        logger.info('Sharing: %s', self.path.relative)

    def get_parameter(self):
        param = create_collaboration_parameter(self.path, self.as_project, self.allow_reshare, self.allow_sync)
        for member in self.members:
            param.shares.append(create_collaborator(member) if isinstance(member, Collaborator) else member)
        return param

    def _execute(self):
        with self.trace_execution():
            return self._function(self._receiver, self.get_parameter())

    async def _a_execute(self):
        with self.trace_execution():
            return await self._function(self._receiver, self.get_parameter())

    def _handle_response(self, r):
        return self.members


def collaborators_from_server_object(server_collaborators):
    collaborators = []
    for collaborator in server_collaborators:
        settings = Object()
        settings._classname = 'ShareConfig'  # pylint: disable=protected-access
        settings.accessMode = collaborator.accessMode
        settings.expiration = collaborator.expiration
        settings.protectionLevel = collaborator.protectionLevel
        settings.invitee = collaborator.invitee
        collaborators.append(settings)
    return collaborators


class AddMembers(Share):

    def __init__(self, function, receiver, path, metadata, new_members):
        collaborators = collaborators_from_server_object(metadata.shares)
        self._new_members = new_members
        super().__init__(function, receiver, path, extend_collaborators(collaborators, new_members), metadata.teamProject,
                         metadata.allowReshare, metadata.shouldSync)

    def _before_command(self):
        logger.info('Granting access for: (%s) to: %s',
                    ', '.join([m.account if isinstance(m.account, str) else m.account.upn for m in self._new_members]),
                    self.path.relative)

    def _execute(self):
        if self._new_members:
            super()._execute()

    async def _a_execute(self):
        if self._new_members:
            await super()._a_execute()


class RemoveMembers(Share):

    def __init__(self, function, receiver, path, metadata, members):
        members, revoke = RemoveMembers._filter_collaborators(metadata.shares, members)
        super().__init__(function, receiver, path, collaborators_from_server_object(members), metadata.teamProject,
                         metadata.allowReshare, metadata.shouldSync)
        self._revoke = revoke

    def _before_command(self):
        logger.info('Revoking access for: (%s) from: %s', ','.join(m.upn for m in self._revoke), self.path.relative)

    def _execute(self):
        if self._revoke:
            super()._execute()

    async def _a_execute(self):
        if self._revoke:
            await super()._a_execute()

    @staticmethod
    def _filter_collaborators(collaborators, accounts):
        current_accounts = obtain_current_accounts(collaborators)
        accounts_to_keep, accounts_to_remove = [], []
        if current_accounts:
            for idx, current_account in enumerate(current_accounts):
                if current_account not in accounts:
                    accounts_to_keep.append(collaborators[idx])
                else:
                    logger.debug('Found member: %s', str(current_account))
                    accounts_to_remove.append(current_account)
            if not accounts_to_remove:
                logger.debug('Member not found: %s', [str(member) for member in accounts])
            else:
                logger.debug('Removing member: %s', [str(account) for account in accounts_to_remove])
        else:
            logger.debug('No members.')
        return accounts_to_keep, accounts_to_remove


class UnShare(Share):

    def __init__(self, function, receiver, path):
        super().__init__(function, receiver, path, [], True, True, True)

    def _before_command(self):
        logger.info('Revoking Share: %s', self.path)

    def _handle_response(self, r):
        return None


class TaskCommand(PortalCommand):

    def __init__(self, function, receiver, block):
        super().__init__(function, receiver)
        self.block = block
        self.background = True

    @abstractmethod
    def _progress_str(self):
        raise NotImplementedError("Subclass must implement the '_progress_str' method")

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

    def _handle_response(self, r):
        if not self.block:
            return r

        if r.completed:
            return self._task_complete(r)

        if r.failed or r.completed_with_warnings:
            return self._task_error(r)

        return r

    def _task_complete(self, task):  # pylint: disable=no-self-use
        return task

    def _task_error(self, task):  # pylint: disable=no-self-use
        return task


class MultiResourceCommand(TaskCommand):

    def __init__(self, function, receiver, block, *paths):
        super().__init__(function, receiver, block)
        self.paths = list(automatic_resolution(paths, receiver.context))

    def get_parameter(self):
        param = ActionResourcesParam.instance()
        for path in self.paths:
            param.add(SrcDstParam.instance(src=path.absolute_encode))
        return param

    def _before_command(self):
        for path in self.paths:
            logger.info('%s: %s', self._progress_str(), path)

    def _task_complete(self, task):
        return [str(path) for path in self.paths]


class Delete(MultiResourceCommand):

    def _progress_str(self):
        return 'Deleting'

    def _task_error(self, task):
        cursor = task.cursor
        raise exceptions.io.core.DeleteError(self.paths, cursor)


class Recover(MultiResourceCommand):

    def _progress_str(self):
        return 'Recovering'

    def _task_error(self, task):
        cursor = task.cursor
        raise exceptions.io.core.RecoverError(self.paths, cursor)


class ResolverCommand(TaskCommand):

    def __init__(self, function, receiver, block, *paths, destination=None, resolver=None, cursor=None):
        super().__init__(function, receiver, block)
        self.paths = list(automatic_resolution(paths, receiver.context))
        self.destination = automatic_resolution(destination, receiver.context)
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
            logger.info('%s: %s to: %s', self._progress_str(), src.relative, dest.relative)

    @abstractmethod
    def _progress_str(self):
        raise NotImplementedError("Subclass must implement the '_progress_str' method")

    def execute(self):
        try:
            return super().execute()
        except (exceptions.io.core.CopyError, exceptions.io.core.MoveError, exceptions.io.core.RenameError) as e:
            if self.resolver:
                return self._try_with_resolver(e.cursor)
            return self._handle_exception(e)

    async def a_execute(self):
        try:
            return await super().a_execute()
        except (exceptions.io.core.CopyError, exceptions.io.core.MoveError, exceptions.io.core.RenameError) as e:
            if self.resolver:
                return await self._a_try_with_resolver(e.cursor)
            return self._handle_exception(e)

    @property
    @abstractmethod
    def _error_object(self):
        raise NotImplementedError('Subclass must implement the "_error_object" property.')

    def _task_error(self, task):
        cursor = task.cursor
        error = self._error_object(self.paths, cursor)

        if task.error_type == ResourceError.Conflict:  # file conflict
            resource = automatic_resolution(cursor.destResource).relative
            raise error from exceptions.io.core.FileConflictError(resource)

        if not task.unknown_object():  # file not found
            resource = automatic_resolution(cursor).relative
            raise error from exceptions.io.core.ObjectNotFoundError(resource)

        if task.progress_str == ResourceError.DestinationNotExists:  # destination directory not found
            directory = self.destination if self.destination is not None else dict(self.paths).get(
                automatic_resolution(cursor.srcResource).relative, None
            )
            raise error from exceptions.io.core.FolderNotFoundError(directory.relative)

        raise self._error_object(self.paths, cursor)


class Copy(ResolverCommand):

    def _progress_str(self):
        return 'Copying'

    def _try_with_resolver(self, cursor):
        return Copy(self._function, self._receiver, self.block, *self.paths,
                    destination=self.destination, resolver=self.resolver, cursor=cursor).execute()

    async def _a_try_with_resolver(self, cursor):
        return await Copy(self._function, self._receiver, self.block, *self.paths,
                          destination=self.destination, resolver=self.resolver, cursor=cursor).a_execute()

    @property
    def _error_object(self):
        return exceptions.io.core.CopyError


class Move(ResolverCommand):

    def _progress_str(self):
        return 'Moving'

    def _try_with_resolver(self, cursor):
        return Move(self._function, self._receiver, self.block, *self.paths,
                    destination=self.destination, resolver=self.resolver, cursor=cursor).execute()

    async def _a_try_with_resolver(self, cursor):
        return await Move(self._function, self._receiver, self.block, *self.paths,
                          destination=self.destination, resolver=self.resolver, cursor=cursor).a_execute()

    @property
    def _error_object(self):
        return exceptions.io.core.MoveError


class Rename(Move):

    def _progress_str(self):
        return 'Renaming'

    def __init__(self, function, receiver, block, path, new_name, resolver, cursor=None):
        super().__init__(function, receiver, block,
                         *[(path, automatic_resolution(path, receiver.context).parent.join(new_name))],
                         resolver=resolver, cursor=cursor
                         )

    def _try_with_resolver(self, cursor):
        source, destination = self.paths[0]
        return Rename(self._function, self._receiver, self.block, source, destination.name,
                      resolver=self.resolver, cursor=cursor).execute()

    async def _a_try_with_resolver(self, cursor):
        source, destination = self.paths[0]
        return await Rename(self._function, self._receiver, self.block, source, destination.name,
                            resolver=self.resolver, cursor=cursor).a_execute()

    @property
    def _error_object(self):
        return exceptions.io.core.RenameError

    def _handle_response(self, r):
        response = super()._handle_response(r)
        return self.paths[0][1].relative if self.block else response
