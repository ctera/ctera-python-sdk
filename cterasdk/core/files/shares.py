import re
import logging
from . import common
from ..enum import ProtectionLevel, CollaboratorType, SearchType, PortalAccountType, FileAccessMode
from ..types import PortalAccount, UserAccount, GroupAccount
from ...common import Object, DateTimeUtils
from ...exceptions import CTERAException


def _search_collaboration_member(core, account, cloud_folder_uid):
    search_param = Object()
    if account.account_type == PortalAccountType.User:
        search_param.searchType = SearchType.Users
    elif account.account_type == PortalAccountType.Group:
        search_param.searchType = SearchType.Groups
    else:
        raise CTERAException("Invalid account type", None, account_type=account.account_type)

    search_param.searchTerm = account.name
    search_param.resourceUid = cloud_folder_uid
    search_param.countLimit = 1
    response = core.api.execute('', 'searchCollaborationMembers', search_param)
    if not response.objects:
        logging.getLogger('cterasdk.core').warning('Could not find results that match your search criteria. %s', {'name': account.name})
    elif len(response.objects) > 1:
        logging.getLogger('cterasdk.core').warning('Search returned multiple results. Skipping...')
    else:
        collaborator = response.objects.pop()
        if account.is_local:
            if account.account_type == PortalAccountType.User and collaborator.type == CollaboratorType.LU:
                logging.getLogger('cterasdk.core').debug('Found local user account. %s', {'name': account.name})
                return collaborator
            if account.account_type == PortalAccountType.Group and collaborator.type == CollaboratorType.LG:
                logging.getLogger('cterasdk.core').debug('Found local group account. %s', {'name': account.name})
                return collaborator
            logging.getLogger('cterasdk.core').warning('Expected to find local %s but found domain %s',
                                                       account.account_type, account.account_type)
        else:
            if account.account_type == PortalAccountType.User and collaborator.type == CollaboratorType.DU:
                logging.getLogger('cterasdk.core').debug('Found domain user account. %s',
                                                         {'name': account.name, 'domain': account.directory})
                return collaborator
            if account.account_type == PortalAccountType.Group and collaborator.type == CollaboratorType.DG:
                logging.getLogger('cterasdk.core').debug('Found domain group account. %s',
                                                         {'name': account.name, 'domain': account.directory})
                return collaborator
            logging.getLogger('cterasdk.core').warning('Expected to find domain %s but found local %s',
                                                       account.account_type, account.account_type)
    return None


def remove_share_recipients(core, path, accounts):
    share_info = get_share_info(core, path)
    current_accounts = _obtain_current_accounts(share_info)

    accounts_to_keep, accounts_to_remove = [], []
    if current_accounts:
        for idx, current_account in enumerate(current_accounts):
            if current_account not in accounts:
                accounts_to_keep.append(share_info.shares[idx])
            else:
                logging.getLogger('cterasdk.core').debug('Found recipient to remove. %s', {'account': str(current_account)})
                accounts_to_remove.append(current_account)
        if not accounts_to_remove:
            logging.getLogger('cterasdk.core').info(
                'Could not find share recipients to remove. %s',
                {
                    'path': str(path.relative),
                    'recipients': [str(member) for member in accounts]
                }
            )
        else:
            share_param = _create_share_param(path.fullpath(), share_info.teamProject, share_info.allowReshare, share_info.shouldSync)
            _update_share_param(share_param, accounts_to_keep)
            logging.getLogger('cterasdk.core').info(
                'Removing share recipients. %s',
                {'path': str(path.relative), 'recipients': [str(account) for account in accounts_to_remove]}
            )
            core.api.execute('', 'shareResource', share_param)
    else:
        logging.getLogger('cterasdk.core').info('Share has no recipients. %s', {'path': str(path.relative)})
    return accounts_to_remove


def get_share_info(core, path):
    return core.api.execute('', 'listShares', path.encoded_fullpath())


def share(core, path, recipients, as_project, allow_reshare, allow_sync):

    if _is_subfolder(path):
        as_project = False  # Can't be a team project
        allow_sync = False  # Can't allow sync of a sub-folder

    valid_recipients = _obtain_valid_recipients(core, path, recipients)
    if valid_recipients:
        share_param = _create_share_param(path.fullpath(), as_project, allow_reshare, allow_sync)
        for recipient in valid_recipients:
            _add_share_recipient(share_param, recipient)

        logging.getLogger('cterasdk.core').info(
            'Sharing item. %s',
            {'path': str(path.relative), 'recipients': [str(recipient) for recipient in valid_recipients]}
        )
        core.api.execute('', 'shareResource', share_param)
        return valid_recipients
    logging.getLogger('cterasdk.core').warning('Resource was not shared. Could not find valid recipients. %s', {'path': str(path.relative)})
    return valid_recipients


def _is_sharing_on_user_behalf(path):
    return re.match(r'^Users/[^/]+(?=/)', path.relative.as_posix()) is not None


def _is_subfolder(path):
    depth = len(path.relative.parts)
    sharing_on_user_behalf = _is_sharing_on_user_behalf(path)
    return (sharing_on_user_behalf and depth > 3) or (not sharing_on_user_behalf and depth > 1)


def add_share_recipients(core, path, recipients):
    share_info = get_share_info(core, path)
    current_accounts = _obtain_current_accounts(share_info)
    valid_recipients = _obtain_valid_recipients(core, path, recipients)
    share_param = _create_share_param(path.fullpath(), share_info.teamProject, share_info.allowReshare, share_info.shouldSync)
    _update_share_param(share_param, share_info.shares)
    accounts_added = []
    if valid_recipients:
        for recipient in valid_recipients:
            if recipient.account not in current_accounts:
                logging.getLogger('cterasdk.core').debug('Found new share recipient. %s', {'recipient': str(recipient.account)})
                _add_share_recipient(share_param, recipient)
                accounts_added.append(recipient)
            else:
                logging.getLogger('cterasdk.core').debug('Share recipient already exists. %s', {'recipient': str(recipient.account)})
        if accounts_added:
            logging.getLogger('cterasdk.core').info(
                'Adding share recipients. %s',
                {'path': str(path.relative), 'recipients': [str(recipient.account) for recipient in accounts_added]}
            )
            core.api.execute('', 'shareResource', share_param)
        else:
            logging.getLogger('cterasdk.core').warning('Could not find new share recipients. %s', {'path': str(path.relative)})
        return accounts_added
    logging.getLogger('cterasdk.core').warning('Share recipients were not added. Could not find valid recipients. %s',
                                               {'path': str(path.relative)})
    return valid_recipients


def _obtain_current_accounts(share_info):
    current_accounts = []
    for collaborator in share_info.shares:
        if collaborator.invitee.type == CollaboratorType.EXT:
            current_accounts.append(collaborator.invitee.email)
        else:
            current_accounts.append(PortalAccount.from_collaborator(collaborator.invitee))
    return current_accounts


def _obtain_valid_recipients(core, path, recipients):
    resource_info = common.get_resource_info(core, path)
    cloud_folder_uid = resource_info.cloudFolderInfo.uid
    valid_recipients = []
    for recipient in recipients:
        if _valid_recipient(recipient):
            if not recipient.type == CollaboratorType.EXT:
                collaborator = _search_collaboration_member(core, recipient.account, cloud_folder_uid)
                if collaborator:
                    recipient.collaborator = collaborator
                    valid_recipients.append(recipient)
            else:
                valid_recipients.append(recipient)
    return valid_recipients


def unshare(core, path):
    resource_info = common.get_resource_info(core, path)
    as_project, allow_reshare, allow_sync = True, True, True

    if _is_subfolder(path):
        as_project = False
        allow_sync = False

    logging.getLogger('cterasdk.core').info(
        'Unsharing %s. %s',
        ('folder' if resource_info.isFolder else 'file'), {'path': str(path.relative)}
    )
    share_param = _create_share_param(path.fullpath(), as_project, allow_reshare, allow_sync)
    return core.api.execute('', 'shareResource', share_param)


def _valid_recipient(recipient):
    valid_recipient = True
    if not recipient.account:
        logging.getLogger('cterasdk.core').warning(
            'No account information found. Skipping. %s',
            {'account': recipient.account}
        )
        valid_recipient = False
    if not isinstance(recipient.account, (str, UserAccount, GroupAccount)):
        logging.getLogger('cterasdk.core').warning(
            'Invalid recipient type. Skipping. %s',
            {'type': type(recipient.account)}
        )
        valid_recipient = False
    if recipient.access not in [v for k, v in FileAccessMode.__dict__.items() if not k.startswith('_')]:
        logging.getLogger('cterasdk.core').warning(
            'Invalid file access mode. Skipping. %s',
            {'account': str(recipient.account), 'access': recipient.access}
        )
        valid_recipient = False
    if recipient.type == CollaboratorType.EXT and not isinstance(recipient.account, str):
        logging.getLogger('cterasdk.core').warning(
            'Invalid external recipient type. Skipping. %s',
            {'expected': 'str', 'actual': type(recipient.account)}
        )
        valid_recipient = False
    if recipient.type in [CollaboratorType.LU, CollaboratorType.LG] and not recipient.account.is_local:
        logging.getLogger('cterasdk.core').warning(
            'Expected local account. Received a domain account. Skipping. %s',
            {'account': str(recipient.account)}
        )
        valid_recipient = False
    if recipient.type in [CollaboratorType.DU, CollaboratorType.DG] and recipient.account.is_local:
        logging.getLogger('cterasdk.core').warning(
            'Expected domain account. Received a local account. Skipping. %s',
            {'account': str(recipient.account)}
        )
        valid_recipient = False
    return valid_recipient


def _create_share_param(url, as_project, allow_reshare, allow_sync):
    share_param = Object()
    share_param._classname = 'ShareResourceParam'  # pylint: disable=protected-access
    share_param.url = url
    share_param.teamProject = as_project
    share_param.allowReshare = allow_reshare
    share_param.shouldSync = allow_sync
    share_param.shares = []
    return share_param


def _update_share_param(share_param, shares):
    for recipient in shares:
        share_config_param = Object()
        share_config_param._classname = 'ShareConfig'  # pylint: disable=protected-access
        share_config_param.accessMode = recipient.accessMode
        share_config_param.expiration = recipient.expiration
        share_config_param.protectionLevel = recipient.protectionLevel
        share_config_param.invitee = recipient.invitee
        share_param.shares.append(share_config_param)
    return share_param


def _add_share_recipient(share_param, recipient):
    share_config_param = Object()
    share_config_param._classname = 'ShareConfig'  # pylint: disable=protected-access
    share_config_param.accessMode = recipient.access
    if not recipient.access == FileAccessMode.NA:
        share_config_param.expiration = recipient.expiration_date
    invitee = None
    if recipient.type == CollaboratorType.EXT:
        invitee = Object()
        invitee._classname = 'Collaborator'  # pylint: disable=protected-access
        invitee.type = recipient.type
        invitee.email = recipient.account
        if recipient.two_factor:
            share_config_param.protectionLevel = ProtectionLevel.Email
        else:
            share_config_param.protectionLevel = ProtectionLevel.Public
    else:
        invitee = recipient.collaborator
    share_config_param.invitee = invitee
    share_param.shares.append(share_config_param)


def create_public_link(core, path, access, expire_in):
    access = {'RO': 'ReadOnly', 'RW': 'ReadWrite', 'PO': 'PreviewOnly'}.get(access)
    expire_on = DateTimeUtils.get_expiration_date(expire_in).strftime('%Y-%m-%d')
    logging.getLogger('cterasdk.core').info('Creating public link. %s',
                                            {'path': str(path.relative), 'access': access, 'expire_on': expire_on})
    param = common.CreateShareParam.instance(path=path.fullpath(), access=access, expire_on=expire_on)
    response = core.api.execute('', 'createShare', param)
    return response.publicLink
