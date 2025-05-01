import logging
from . import io
from ..enum import CollaboratorType
from ...cio import core as fs


logger = logging.getLogger('cterasdk.core')


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
    resource_info = io.root(core, path)
    cloud_folder_uid = resource_info.cloudFolderInfo.uid
    valid_recipients = []
    for recipient in recipients:
        if fs.valid_recipient(recipient):
            if not recipient.type == CollaboratorType.EXT:
                collaborator = _search_collaboration_member(core, recipient.account, cloud_folder_uid)
                if collaborator:
                    recipient.collaborator = collaborator
                    valid_recipients.append(recipient)
            else:
                valid_recipients.append(recipient)
    return valid_recipients


def unshare(core, path):
    resource_info = io.root(core, path)
    with fs.unshare(resource_info, path) as param:
        return core.api.execute('', 'shareResource', param)


def public_link(core, path, access, expire_in):
    with fs.public_link(path, access, expire_in) as param:
        response = core.api.execute('', 'createShare', param)
    return response.publicLink
