import logging

from .base_command import BaseCommand
from ..common import Object
from ..exception import CTERAException
from .enum import PortalAccountType, SearchType


class DirectoryService(BaseCommand):
    """
    Portal Active Directory APIs
    """

    def fetch(self, active_directory_accounts):
        """
        Instruct the Portal to fetch the provided Active Directory Accounts

        :param list[cterasdk.core.types.PortalAccount] active_directory_accounts: List of Active Directory Accounts to fetch

        :return: Response Code
        """
        domains = self._portal.users.list_domains()
        account_types = [v for k, v in PortalAccountType.__dict__.items() if not k.startswith('_')]

        param = []
        for active_directory_account in active_directory_accounts:
            if active_directory_account.directory not in domains:
                logging.getLogger().error('Invalid domain name. %s', {'domain': active_directory_account.directory})
                raise CTERAException('Invalid domain', None, domain=active_directory_account.directory, domains=domains)

            if active_directory_account.account_type not in account_types:
                logging.getLogger().error('Invalid account type. %s', {'type': active_directory_account.account_type})
                raise CTERAException('Invalid account type', None, type=active_directory_account.account_type, options=account_types)

        for active_directory_account in active_directory_accounts:
            if active_directory_account.account_type == PortalAccountType.User:
                param.append(self._search_users(active_directory_account.directory, active_directory_account.name))
            elif active_directory_account.account_type == PortalAccountType.Group:
                param.append(self._search_groups(active_directory_account.directory, active_directory_account.name))

        logging.getLogger().info('Starting to fetch users and groups.')

        response = self._portal.execute('', 'syncAD', param)

        logging.getLogger().info('Started fetching users and groups.')

        return response

    def _search_users(self, domain, user):
        return self._search_directory_services(SearchType.Users, domain, user)

    def _search_groups(self, domain, group):
        return self._search_directory_services(SearchType.Groups, domain, group)

    def _search_directory_services(self, search_type, domain, name):
        param = Object()
        param.mode = search_type
        param.name = name
        param.domain = domain

        logging.getLogger().info(
            'Searching %(search_type)s: %(info)s',
            dict(search_type=search_type, info={'domain': domain, 'name': name})
        )

        objects = self._portal.execute('', 'searchAD', param)
        if not objects:
            logging.getLogger().info('Could not find results that match your search criteria. %s', {'domain': domain, 'name': name})
            raise CTERAException(
                'Could not find results that match your search criteria',
                None,
                domain=domain,
                type=search_type,
                account=name
            )

        for principal in objects:
            if principal.name == name:
                logging.getLogger().info('Found. %s', {'domain': domain, 'name': name})
                return principal

        raise CTERAException(
            'Search returned multiple results, but none that match your search criteria',
            None,
            domain=domain,
            type=search_type,
            account=name
        )
