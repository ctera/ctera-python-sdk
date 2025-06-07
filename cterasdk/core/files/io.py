import logging
from ...cio.common import encode_request_parameter
from ...cio import core as fs
from ...exceptions.io import ResourceNotFoundError, ResourceExistsError, NotADirectory
from ...core import query
from ..enum import CollaboratorType
from ...lib import FetchResourcesResponse


logger = logging.getLogger('cterasdk.core')


def listdir(core, path, depth=None, include_deleted=False, search_criteria=None, limit=None):
    with fs.fetch_resources(path, depth, include_deleted, search_criteria, limit) as param:
        if param.depth > 0:
            return query.iterator(core, '', param, 'fetchResources', callback_response=FetchResourcesResponse)
        return core.api.execute('', 'fetchResources', param)


def exists(core, path):
    present, *_ = metadata(core, path, suppress_error=True)
    return present


def metadata(core, path, suppress_error=False):
    """
    Get item metadata.

    :returns: A tuple indicating if a file exists, and its metadata
    """
    response = listdir(core, path, 0)
    if response.root is None:
        if not suppress_error:
            raise ResourceNotFoundError(path.absolute)
        return False, None
    return True, response.root


def versions(core, path):
    with fs.versions(path):
        return core.api.execute('', 'listSnapshots', path.absolute)


def walk(core, scope, path, include_deleted=False):
    paths = [fs.CorePath.instance(scope, path)]
    while len(paths) > 0:
        path = paths.pop(0)
        entries = listdir(core, path, include_deleted=include_deleted)
        for e in entries:
            if e.isFolder:
                paths.append(fs.CorePath.instance(scope, e))
            yield e


def mkdir(core, path):
    with fs.makedir(path) as param:
        response = core.api.execute('', 'makeCollection', param)
    fs.accept_response(response, path.reference.as_posix())


def makedirs(core, path):
    directories = path.parts
    for i in range(1, len(directories) + 1):
        path = fs.CorePath.instance(path.scope, '/'.join(directories[:i]))
        try:
            mkdir(core, path)
        except ResourceExistsError:
            logger.debug('Resource already exists: %s', path.reference.as_posix())


def rename(core, path, name):
    with fs.rename(path, name) as param:
        return core.api.execute('', 'moveResources', param)


def remove(core, *paths):
    with fs.delete(*paths) as param:
        return core.api.execute('', 'deleteResources', param)


def recover(core, *paths):
    with fs.recover(*paths) as param:
        return core.api.execute('', 'restoreResources', param)


def copy(core, *paths, destination=None):
    with fs.copy(*paths, destination=destination) as param:
        return core.api.execute('', 'copyResources', param)


def move(core, *paths, destination=None):
    with fs.move(*paths, destination=destination) as param:
        return core.api.execute('', 'moveResources', param)


def ensure_directory(core, directory, suppress_error=False):
    present, resource = metadata(core, directory, suppress_error=True)
    if (not present or not resource.isFolder) and not suppress_error:
        raise NotADirectory(directory.absolute)
    return resource.isFolder if present else False, resource


def handle(path):
    """
    Create function to retrieve file handle.

    :param cterasdk.cio.edge.CorePath path: Path to file.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    def wrapper(core):
        """
        Get file handle.

        :param cterasdk.objects.synchronous.core.Portal core: Portal object.
        """
        with fs.handle(path) as param:
            return core.io.download(param)
    return wrapper


def handle_many(directory, *objects):
    """
    Create function to retrieve zip archive

    :param cterasdk.cio.edge.CorePath directory: Path to directory.
    :param args objects: List of files and folders.
    :returns: Callable function to retrieve file handle.
    :rtype: callable
    """
    def wrapper(core):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.core.Portal core: Portal object.
        :param str name: File name.
        :param object handle: File handle.
        """
        with fs.handle_many(directory, objects) as param:
            _, resource = ensure_directory(core, directory)
            return core.io.download_zip(str(resource.cloudFolderInfo.uid), encode_request_parameter(param))
    return wrapper


def _validate_destination(core, name, destination):
    is_dir, resource = ensure_directory(core, destination, suppress_error=True)
    if not is_dir:
        is_dir, resource = ensure_directory(core, destination.parent)
        return resource.cloudFolderInfo.uid, destination.name, destination.parent
    return resource.cloudFolderInfo.uid, name, destination


def upload(name, size, destination, fd):
    """
    Create upload function

    :param str name: File name.
    :param cterasdk.cio.core.CorePath destination: Path to directory.
    :param object fd: File handle.
    :returns: Callable function to start the upload.
    :rtype: callable
    """
    def wrapper(core):
        """
        Upload file from metadata and file handle.

        :param cterasdk.objects.synchronous.core.Portal core: Portal object.
        """
        uid, filename, directory = _validate_destination(core, name, destination)
        with fs.upload(core, filename, directory, size, fd) as param:
            return core.io.upload(str(uid), param)
    return wrapper


def _search_collaboration_member(core, account, cloud_folder_uid):
    with fs.search_collaboration_member(account, cloud_folder_uid) as param:
        response = core.api.execute('', 'searchCollaborationMembers', param)
    return fs.consume_search_collaboration_response(response, account)


def remove_share_recipients(core, path, accounts):
    share_info = get_share_info(core, path)
    current_accounts = fs.obtain_current_accounts(share_info)
    accounts_to_keep, accounts_to_remove = fs.find_recipients_to_remove(share_info, path, current_accounts, accounts)
    if accounts_to_remove:
        with fs.share(path, share_info.teamProject, share_info.allowReshare, share_info.shouldSync, accounts_to_keep) as param:
            core.api.execute('', 'shareResource', param)
    return accounts_to_remove


def get_share_info(core, path):
    with fs.share_info(path) as param:
        return core.api.execute('', 'listShares', param)


def share(core, path, recipients, as_project, allow_reshare, allow_sync):
    valid_recipients = _obtain_valid_recipients(core, path, recipients)
    if valid_recipients:
        with fs.share(path, as_project, allow_reshare, allow_sync) as param:
            for recipient in valid_recipients:
                fs.add_share_recipient(param, recipient)
            logger.info('Sharing: %s with: %s', path.reference.as_posix(), [str(recipient) for recipient in valid_recipients])
            core.api.execute('', 'shareResource', param)
            return valid_recipients
    logger.warning('Resource not shared. Could not find valid recipients: %s', path.reference.as_posix())
    return valid_recipients


def add_share_recipients(core, path, recipients):
    share_info = get_share_info(core, path)
    current_accounts = fs.obtain_current_accounts(share_info)
    valid_recipients = _obtain_valid_recipients(core, path, recipients)
    with fs.share(path, share_info.teamProject, share_info.allowReshare, share_info.shouldSync, share_info.shares) as param:
        accounts_to_add = fs.find_recipients_to_add(path, share_info, current_accounts, valid_recipients)
        if accounts_to_add:
            for recipient in accounts_to_add:
                fs.add_share_recipient(param, recipient)
            core.api.execute('', 'shareResource', param)
    return valid_recipients


def _obtain_valid_recipients(core, path, recipients):
    _, resource_info = metadata(core, path)
    valid_recipients = []
    for recipient in filter(fs.valid_recipient, recipients):
        if not recipient.type == CollaboratorType.EXT:
            collaborator = _search_collaboration_member(core, recipient.account, resource_info.cloudFolderInfo.uid)
            if collaborator:
                recipient.collaborator = collaborator
                valid_recipients.append(recipient)
        else:
            valid_recipients.append(recipient)
    return valid_recipients


def unshare(core, path):
    _, resource_info = metadata(core, path)
    with fs.unshare(resource_info, path) as param:
        return core.api.execute('', 'shareResource', param)


def public_link(core, path, access, expire_in):
    with fs.public_link(path, access, expire_in) as param:
        response = core.api.execute('', 'createShare', param)
    return response.publicLink
