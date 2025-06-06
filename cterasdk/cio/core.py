import re
import logging
from contextlib import contextmanager
from ..objects.uri import quote, unquote
from ..common import Object, DateTimeUtils
from ..core.enum import ProtectionLevel, CollaboratorType, SearchType, PortalAccountType, FileAccessMode
from ..core.types import PortalAccount, UserAccount, GroupAccount
from ..exceptions.io import ResourceExistsError, PathValidationError, NameSyntaxError, ReservedNameError
from . import common


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
        reference = self.reference.as_posix()
        previous_versions = 'PreviousVersions/'
        if previous_versions in reference:
            index = reference.index(previous_versions) + len(previous_versions)
            return f'{self.scope.as_posix()}/{quote(reference[:index]) + reference[index:]}'
        return super().absolute

    @staticmethod
    def instance(scope, entries):
        if isinstance(entries, list):
            return [CorePath(scope, e) for e in entries]
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


@contextmanager
def fetch_resources(path, depth, include_deleted, search_criteria, limit):
    """
    Create List Directory Parameter.
    """
    depth = depth if depth is not None else 1
    builder = FetchResourcesParamBuilder().root(path.absolute_encode).depth(depth)
    if include_deleted:
        builder.include_deleted()
    if search_criteria:
        builder.searchCriteria(search_criteria)
    if limit:
        builder.limit(limit)
    logger.info('Listing directory: %s', path.reference.as_posix())
    yield builder.build()


@contextmanager
def versions(path):
    logger.info('Listing versions: %s', path.reference.as_posix())
    yield


@contextmanager
def makedir(path):
    param = Object()
    param.name = path.name
    param.parentPath = path.parent.absolute_encode
    logger.info('Creating directory: %s', path.reference.as_posix())
    yield param
    logger.info('Directory created: %s', path.reference.as_posix())


@contextmanager
def rename(path, name):
    param = ActionResourcesParam.instance()
    param.add(SrcDstParam.instance(src=path.absolute, dest=path.parent.join(name).absolute))
    logger.info('Renaming item: %s to: %s', path.reference.as_posix(), name)
    yield param


def _delete_or_recover(paths, *, message=None):
    param = ActionResourcesParam.instance()
    paths = [paths] if not isinstance(paths, list) else paths
    for path in paths:
        param.add(SrcDstParam.instance(src=path.absolute))
        if message:
            logger.info('%s: %s', message, path.reference.as_posix())
    yield param


@contextmanager
def delete(*paths):
    return _delete_or_recover(list(paths), message='Deleting item')


@contextmanager
def recover(*paths):
    return _delete_or_recover(list(paths), message='Recovering item')


def _copy_or_move(paths, destination, *, message=None):
    param = ActionResourcesParam.instance()
    paths = [paths] if not isinstance(paths, list) else paths
    for path in paths:
        param.add(SrcDstParam.instance(src=path.absolute, dest=destination.join(path.name).absolute))
        if message:
            logger.info('%s from: %s to: %s', message, path.reference.as_posix(), destination.join(path.name).reference.as_posix())
    yield param


@contextmanager
def copy(*paths, destination=None):
    return _copy_or_move(list(paths), destination, message='Copying item')


@contextmanager
def move(*paths, destination=None):
    return _copy_or_move(list(paths), destination, message='Moving item')


@contextmanager
def public_link(path, access, expire_in):
    access = {'RO': 'ReadOnly', 'RW': 'ReadWrite', 'PO': 'PreviewOnly'}.get(access)
    expire_on = DateTimeUtils.get_expiration_date(expire_in).strftime('%Y-%m-%d')
    logger.info('Creating Public Link for: %s. Access: %s. Expires: %s', path.reference.as_posix(), access, expire_on)
    param = CreateShareParam.instance(path=path.absolute, access=access, expire_on=expire_on)
    yield param


@contextmanager
def handle(path):
    logger.info('Getting file handle: %s', path.reference)
    yield path.reference


@contextmanager
def upload(core, name, destination, size, fd):
    fd, size = common.encode_stream(fd, size)
    param = dict(
        name=name,
        Filename=name,
        fullpath=core.io.builder(CorePath(destination.reference, name).absolute_encode),
        fileSize=size,
        file=fd
    )
    logger.info('Uploading: %s to: %s', name, destination.reference)
    yield param


@contextmanager
def handle_many(directory, objects):
    param = Object()
    param.paths = ['/'.join([directory.absolute, filename]) for filename in objects]
    param.snapshot = None
    param.password = None
    param.portalName = None
    param.showDeleted = False
    logger.info('Getting directory handle: %s', directory.reference)
    yield param


@contextmanager
def share_info(path):
    logger.info('Getting Share info: %s', path.reference.as_posix())
    yield path.absolute_encode


def _is_sharing_on_user_behalf(path):
    return re.match(r'^Users/[^/]+(?=/)', path.reference.as_posix()) is not None


def _is_subfolder(path):
    depth = len(path.reference.parts)
    sharing_on_user_behalf = _is_sharing_on_user_behalf(path)
    return (sharing_on_user_behalf and depth > 3) or (not sharing_on_user_behalf and depth > 1)


@contextmanager
def share(path, as_project, allow_reshare, allow_sync, shares=None):
    if _is_subfolder(path):
        as_project = False  # Can't be a team project
        allow_sync = False  # Can't allow sync of a sub-folder

    param = Object()
    param._classname = 'ShareResourceParam'  # pylint: disable=protected-access
    param.url = path.absolute
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

    yield param


@contextmanager
def unshare(resource_info, path):
    with share(path, True, True, True) as param:
        logger.info("Unsharing %s: %s", ('folder' if resource_info.isFolder else 'file'), path.reference.as_posix())
        yield param


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
            logger.info('Share recipients not found: %s', [str(member) for member in accounts])
        else:
            logger.info('Removing share recipients: %s', [str(account) for account in accounts_to_remove])
    else:
        logger.info('Share has no recipients. %s', path.reference.as_posix())
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
            logger.info('Adding share recipients: %s', [str(recipient.account) for recipient in accounts_to_add])
        else:
            logger.warning('Could not find new share recipients: %s', path.reference.as_posix())
        return accounts_to_add
    logger.warning('Could not find valid share recipients: %s', path.reference.as_posix())
    return accounts_to_add


@contextmanager
def search_collaboration_member(account, cloud_folder_uid):
    param = Object()
    if account.account_type == PortalAccountType.User:
        param.searchType = SearchType.Users
    elif account.account_type == PortalAccountType.Group:
        param.searchType = SearchType.Groups
    else:
        raise ValueError(f'Invalid account type: {account.account_type}')

    param.searchTerm = account.name
    param.resourceUid = cloud_folder_uid
    param.countLimit = 1
    logger.info('Searching for member: %s', str(account))
    yield param


def consume_search_collaboration_response(response, account):
    if not response.objects:
        logger.warning('Could not find results that match your search criteria. %s', {'name': account.name})
    elif len(response.objects) > 1:
        logger.warning('Search returned multiple results. Skipping...')
    else:
        collaborator = response.objects.pop()
        if account.is_local:
            if account.account_type == PortalAccountType.User and collaborator.type == CollaboratorType.LU:
                logger.debug('Found local user account. %s', {'name': account.name})
                return collaborator
            if account.account_type == PortalAccountType.Group and collaborator.type == CollaboratorType.LG:
                logger.debug('Found local group account. %s', {'name': account.name})
                return collaborator
            logger.warning('Expected to find local %s but found domain %s', account.account_type, account.account_type)
        else:
            if account.account_type == PortalAccountType.User and collaborator.type == CollaboratorType.DU:
                logger.debug('Found domain user account. %s', {'name': account.name, 'domain': account.directory})
                return collaborator
            if account.account_type == PortalAccountType.Group and collaborator.type == CollaboratorType.DG:
                logger.debug('Found domain group account. %s', {'name': account.name, 'domain': account.directory})
                return collaborator
            logger.warning('Expected to find domain %s but found local %s', account.account_type, account.account_type)
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


def accept_response(response, reference):
    """
    Check if response contains an error.
    """
    error = {
        "FileWithTheSameNameExist": ResourceExistsError(),
        "DestinationNotExists": PathValidationError(),
        "InvalidName": NameSyntaxError(),
        "ReservedName": ReservedNameError()
    }.get(response, None)
    try:
        if error:
            raise error
    except ResourceExistsError as error:
        logger.info('Resource already exists: a file or folder with this name already exists. %s', {'path': reference})
        raise error
    except PathValidationError as error:
        logger.error('Path validation failed: the specified destination path does not exist. %s', {'path': reference})
        raise error
    except NameSyntaxError as error:
        logger.error('Invalid name: the name contains characters that are not allowed. %s', {'name': reference})
        raise error
    except ReservedNameError as error:
        logger.error('Reserved name error: the name is reserved and cannot be used. %s', {'name': reference})
        raise error
