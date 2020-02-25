import logging

from .base_command import BaseCommand
from ..common import Object
from ..exception import CTERAException, InputError
from .enum import ActiveDirectoryAccountType, SearchType


class DirectoryService(BaseCommand):

    def fetch(self, tuples):
        domains = self._portal.users.domains()
        account_types = [v for k, v in ActiveDirectoryAccountType.__dict__.items() if not k.startswith('_')]

        param = []
        for entry in tuples:
            if len(entry) != 3:
                logging.getLogger().error('Invalid entry length.')
                raise InputError('Invalid entry', entry, '[("domain", "account_type", "account_name"), ...]')

            domain, account_type, name = entry
            if domain not in domains:
                logging.getLogger().error('Invalid domain name. %s', {'domain': domain})
                raise CTERAException('Invalid domain', None, domain=domain, domains=domains)

            if account_type not in account_types:
                logging.getLogger().error('Invalid account type. %s', {'type': account_type})
                raise CTERAException('Invalid account type', None, type=account_type, options=account_types)

        for domain, account_type, name in tuples:
            if account_type == ActiveDirectoryAccountType.User:
                param.append(self._search_users(domain, name))
            elif account_type == ActiveDirectoryAccountType.Group:
                param.append(self._search_groups(domain, name))

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
