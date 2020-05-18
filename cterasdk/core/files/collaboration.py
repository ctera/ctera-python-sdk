import logging
from . import common
from ..enum import ProtectionLevel, CollaboratorType, SearchType, PortalAccountType, FileAccessMode
from ..types import PortalAccount, UserAccount, GroupAccount
from ...common import Object
from ...exception import CTERAException


def _search_collaboration_member(ctera_host, account, cloud_folder_uid):
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
    response = ctera_host.execute('', 'searchCollaborationMembers', search_param)
    if not response.objects:
        logging.getLogger().warning('Could not find results that match your search criteria. %s', {'name': account.name})
    elif len(response.objects) > 1:
        logging.getLogger().warning('Search returned multiple results. Skipping...')
    else:
        collaborator = response.objects.pop()
        if account.is_local:
            if account.account_type == PortalAccountType.User and collaborator.type == CollaboratorType.LU:
                logging.getLogger().debug('Found local user account. %s', {'name': account.name})
                return collaborator
            if account.account_type == PortalAccountType.Group and collaborator.type == CollaboratorType.LG:
                logging.getLogger().debug('Found local group account. %s', {'name': account.name})
                return collaborator
            logging.getLogger().warning('Expected to find local %s but found domain %s', account.account_type, account.account_type)
        else:
            if account.account_type == PortalAccountType.User and collaborator.type == CollaboratorType.DU:
                logging.getLogger().debug('Found domain user account. %s', {'name': account.name, 'domain': account.directory})
                return collaborator
            if account.account_type == PortalAccountType.Group and collaborator.type == CollaboratorType.DG:
                logging.getLogger().debug('Found domain group account. %s', {'name': account.name, 'domain': account.directory})
                return collaborator
            logging.getLogger().warning('Expected to find domain %s but found local %s', account.account_type, account.account_type)
    return None


def remove_share_recipients(ctera_host, path, accounts):
    share_info = get_share_info(ctera_host, path)
    current_accounts = _obtain_current_accounts(share_info)

    accounts_to_keep, accounts_to_remove = [], []
    if current_accounts:
        for idx, current_account in enumerate(current_accounts):
            if current_account not in accounts:
                accounts_to_keep.append(share_info.shares[idx])
            else:
                logging.getLogger().debug('Found recipient to remove. %s', {'account': str(current_account)})
                accounts_to_remove.append(current_account)
        if not accounts_to_remove:
            logging.getLogger().info(
                'Could not find share recipients to remove. %s',
                {
                    'path': str(path.relativepath),
                    'recipients': [str(member) for member in accounts]
                }
            )
        else:
            share_param = _create_share_param(path.fullpath(), share_info.teamProject, share_info.allowReshare, share_info.shouldSync)
            _update_share_param(share_param, accounts_to_keep)
            logging.getLogger().info(
                'Removing share recipients. %s',
                {'path': str(path.relativepath), 'recipients': [str(account) for account in accounts_to_remove]}
            )
            ctera_host.execute('', 'shareResource', share_param)
    else:
        logging.getLogger().info('Share has no recipients. %s', {'path': str(path.relativepath)})
    return accounts_to_remove


def get_share_info(ctera_host, path):
    return ctera_host.execute('', 'listShares', path.encoded_fullpath())


def share(ctera_host, path, recipients, as_project, allow_reshare, allow_sync):
    if len(path.relativepath.parts) > 1:  # The shared path is not a cloud folder. Therefore, the following attrs aren't customizable.
        as_project = False
        allow_sync = False

    valid_recipients = _obtain_valid_recipients(ctera_host, path, recipients)
    if valid_recipients:
        share_param = _create_share_param(path.fullpath(), as_project, allow_reshare, allow_sync)
        for recipient in valid_recipients:
            _add_share_recipient(share_param, recipient)

        logging.getLogger().info(
            'Sharing item. %s',
            {'path': str(path.relativepath), 'recipients': [str(recipient) for recipient in valid_recipients]}
        )
        ctera_host.execute('', 'shareResource', share_param)
        return valid_recipients
    logging.getLogger().warning('Resource was not shared. Could not find valid recipients. %s', {'path': str(path.relativepath)})
    return valid_recipients


def add_share_recipients(ctera_host, path, recipients):
    share_info = get_share_info(ctera_host, path)
    current_accounts = _obtain_current_accounts(share_info)
    valid_recipients = _obtain_valid_recipients(ctera_host, path, recipients)
    share_param = _create_share_param(path.fullpath(), share_info.teamProject, share_info.allowReshare, share_info.shouldSync)
    _update_share_param(share_param, share_info.shares)
    accounts_added = []
    if valid_recipients:
        for recipient in valid_recipients:
            if recipient.account not in current_accounts:
                logging.getLogger().debug('Found new share recipient. %s', {'recipient': str(recipient.account)})
                _add_share_recipient(share_param, recipient)
                accounts_added.append(recipient)
            else:
                logging.getLogger().debug('Share recipient already exists. %s', {'recipient': str(recipient.account)})
        if accounts_added:
            logging.getLogger().info(
                'Adding share recipients. %s',
                {'path': str(path.relativepath), 'recipients': [str(recipient.account) for recipient in accounts_added]}
            )
            ctera_host.execute('', 'shareResource', share_param)
        else:
            logging.getLogger().warning('Could not find new share recipients. %s', {'path': str(path.relativepath)})
        return accounts_added
    logging.getLogger().warning('Share recipients were not added. Could not find valid recipients. %s', {'path': str(path.relativepath)})
    return valid_recipients


def _obtain_current_accounts(share_info):
    current_accounts = []
    for collaborator in share_info.shares:
        if collaborator.invitee.type == CollaboratorType.EXT:
            current_accounts.append(collaborator.invitee.email)
        else:
            current_accounts.append(PortalAccount.from_collaborator(collaborator.invitee))
    return current_accounts


def _obtain_valid_recipients(ctera_host, path, recipients):
    resource_info = common.get_resource_info(ctera_host, path)
    cloud_folder_uid = resource_info.cloudFolderInfo.uid
    valid_recipients = []
    for recipient in recipients:
        if _valid_recipient(recipient):
            if not recipient.type == CollaboratorType.EXT:
                collaborator = _search_collaboration_member(ctera_host, recipient.account, cloud_folder_uid)
                if collaborator:
                    recipient.collaborator = collaborator
                    valid_recipients.append(recipient)
            else:
                valid_recipients.append(recipient)
    return valid_recipients


def unshare(ctera_host, path):
    resource_info = common.get_resource_info(ctera_host, path)
    as_project, allow_reshare, allow_sync = True, True, True
    if len(path.relativepath.parts) > 1:  # The shared path is not a cloud folder. Therefore, the following attrs aren't customizable.
        as_project = False
        allow_sync = False

    logging.getLogger().info(
        'Unsharing %s. %s',
        ('folder' if resource_info.isFolder else 'file'), {'path': str(path.relativepath)}
    )
    share_param = _create_share_param(path.fullpath(), as_project, allow_reshare, allow_sync)
    return ctera_host.execute('', 'shareResource', share_param)


def _valid_recipient(recipient):
    valid_recipient = True
    if not recipient.account:
        logging.getLogger().warning(
            'No account information found. Skipping. %s',
            {'account': recipient.account}
        )
        valid_recipient = False
    if not isinstance(recipient.account, (str, UserAccount, GroupAccount)):
        logging.getLogger().warning(
            'Invalid recipient type. Skipping. %s',
            {'type': type(recipient.account)}
        )
        valid_recipient = False
    if recipient.access not in [v for k, v in FileAccessMode.__dict__.items() if not k.startswith('_')]:
        logging.getLogger().warning(
            'Invalid file access mode. Skipping. %s',
            {'account': str(recipient.account), 'access': recipient.access}
        )
        valid_recipient = False
    if recipient.type == CollaboratorType.EXT and not isinstance(recipient.account, str):
        logging.getLogger().warning(
            'Invalid external recipient type. Skipping. %s',
            {'expected': 'str', 'actual': type(recipient.account)}
        )
        valid_recipient = False
    if recipient.type in [CollaboratorType.LU, CollaboratorType.LG] and not recipient.account.is_local:
        logging.getLogger().warning(
            'Expected local account. Received a domain account. Skipping. %s',
            {'account': str(recipient.account)}
        )
        valid_recipient = False
    if recipient.type in [CollaboratorType.DU, CollaboratorType.DG] and recipient.account.is_local:
        logging.getLogger().warning(
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
