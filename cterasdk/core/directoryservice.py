import logging

from .base_command import BaseCommand
from ..common import Object
from ..exceptions import CTERAException
from .enum import PortalAccountType, SearchType, DirectoryServiceType, DirectoryServiceFetchMode, Role, DirectorySearchEntityType
from .types import AccessControlEntry, AccessControlRule, UserAccount, GroupAccount


class DirectoryService(BaseCommand):
    """
    Portal Active Directory APIs
    """

    def _get_configuration(self):
        return self._core.api.get('/directoryConnector')

    def connected(self):
        directory_services_config = self._get_configuration()
        if directory_services_config is None:
            return False
        try:
            self._connect_to_directory_services(directory_services_config)
            return True
        except CTERAException:
            return False

    # pylint: disable=too-many-arguments
    def connect(self, domain, username, password, directory=DirectoryServiceType.Microsoft,
                domain_controllers=None, ou=None, ssl=False, krb=False, mapping=None, acl=None,
                default=Role.Disabled, fetch=DirectoryServiceFetchMode.Lazy):
        """
        Connect a Portal tenant to directory services

        :param str domain: The directory services domain to connect to
        :param str username: The user name to use when connecting to the active directory services
        :param str password: The password to use when connecting to the active directory services
        :param str,optional ou: The OU path to use when connecting to the active directory services, defaults to `None`
        :param cterasdk.core.enum.DirectoryServiceType,optional directory: The directory service type, deafults to `'ActiveDirectory'`
        :param cterasdk.core.types.DomainControllers,optional domain_controllers:
            Connect to a primary and a secondary domain controllers, defaults to `None`
        :param bool,optional ssl: Connect using SSL, defaults to `False`
        :param bool,optional krb: Connect using Kerberos, defaults to `False`
        :param list[cterasdk.common.types.ADDomainIDMapping],optional: The directory services UID/GID mapping
        :param list[cterasdk.core.types.AccessControlEntry],optional acl: List of access control entries and their associated roles
        :param cterasdk.core.enum.Role default: Default role if no match applies, defaults to `None`
        :param str,optional fetch: Configure identity fetching mode, defaults to `'Lazy'`
        """
        param = Object()
        param._classname = 'ActiveDirectory'  # pylint: disable=protected-access
        param.type = directory
        param.domain = domain
        param.useKerberos = krb
        param.useSSL = ssl
        param.username = username
        param.password = password
        param.ou = ou
        param.noMatchRole = default
        param.accessControlRules = None
        param.idMapping = None
        param.fetchMode = fetch
        param.ipAddresses = None

        if domain_controllers:
            param.ipAddresses = Object()
            param.ipAddresses._classname = 'DomainControlIPAddresses'  # pylint: disable=protected-access
            param.ipAddresses.ipAddress1 = domain_controllers.primary
            param.ipAddresses.ipAddress2 = domain_controllers.secondary

        tenant = self._core.session().account.tenant
        logging.getLogger('cterasdk.core').info('Connecting Portal to directory services. %s', {
            'tenant': tenant,
            'type': type,
            'domain': domain
        })
        self._connect_to_directory_services(param)
        logging.getLogger('cterasdk.core').info('Connected Portal to directory services. %s', {'tennat': tenant, 'domain': domain})

        if mapping:
            self._configure_advanced_mapping(mapping)

        if acl:
            self._configure_access_control(acl, default)

    def _connect_to_directory_services(self, param):
        return self._core.api.execute('', 'testAndSaveAD', param)

    def get_advanced_mapping(self):
        """
        Retrieve directory services advanced mapping configuration

        :returns: A dictionary of domain mapping objects
        :rtype: dict
        """
        return {map.domainFlatName: map for map in self._core.api.get('/directoryConnector/idMapping/map')}

    def set_advanced_mapping(self, mapping):
        """
        Configure advanced mapping

        :param list[cterasdk.common.types.ADDomainIDMapping] mapping: List of domains and their UID/GID mapping range
        """
        if self._get_configuration() is None:
            raise CTERAException('Failed to apply mapping. Not connected to directory services.')

        return self._configure_advanced_mapping(mapping)

    def _configure_advanced_mapping(self, mapping):
        param = Object()
        param._classname = 'ADIDMapping'  # pylint: disable=protected-access
        param.map = mapping
        logging.getLogger('cterasdk.core').debug('Updating advanced mapping. %s', {
            'domains': [mapping.domainFlatName for mapping in param.map]
        })
        response = self._core.api.put('/directoryConnector/idMapping', param)
        logging.getLogger('cterasdk.core').info('Updated advanced mapping.')
        return response

    def get_access_control(self):
        """
        Retrieve directory services access control list

        :returns: List of access control entries
        :rtype: list[cterasdk.core.types.AccessControlEntry]
        """
        acl = []
        for ace in self._core.api.get('/directoryConnector/accessControlRules'):
            if ace.group.type == DirectorySearchEntityType.User:
                acl.append(AccessControlEntry(UserAccount(ace.group.name, ace.group.domain), ace.role))
            elif ace.group.type == DirectorySearchEntityType.Group:
                acl.append(AccessControlEntry(GroupAccount(ace.group.name, ace.group.domain), ace.role))
        return acl

    def set_access_control(self, acl=None, default=None):
        """
        Configure directory services access control

        :param list[cterasdk.core.types.AccessControlEntry],optional acl:
            List of access control entries and their associated roles
        :param cterasdk.core.enum.Role default: Default role if no match applies, defaults to `None`
        """
        directory_services_config = self._get_configuration()
        if directory_services_config is None:
            raise CTERAException('Failed to apply access control. Not connected to directory services.')

        default = default if default is not None else directory_services_config.noMatchRole
        return self._configure_access_control(acl, default)

    def _configure_access_control(self, acl, default=None):

        access_control_rules = []
        for ace in acl:
            account = None
            if ace.account.account_type == PortalAccountType.User:
                account = self._search_users(ace.account.directory, ace.account.name)
            elif ace.account.account_type == PortalAccountType.Group:
                account = self._search_groups(ace.account.directory, ace.account.name)
            access_control_rules.append(AccessControlRule(account, ace.role))

        logging.getLogger('cterasdk.core').info('Updating access control rules.')
        response = self._core.api.put('/directoryConnector/accessControlRules', access_control_rules)
        logging.getLogger('cterasdk.core').info('Updated access control rules.')

        if default is not None:
            logging.getLogger('cterasdk.core').info('Updating default role.')
            response = self._core.api.put('/directoryConnector/noMatchRole', default)
            logging.getLogger('cterasdk.core').info('Updated default role')

        return response

    def get_default_role(self):
        """
        Retrieve the default role assigned when no access control entry match was found
        """
        return self._core.api.get('/directoryConnector/noMatchRole')

    def get_connected_domain(self):
        """
        Get the connected domain information. Returns `None` if the Portal tenant is not connected to a domain

        :return str: The connected domain
        """
        domain = None
        try:
            domain = self._core.api.get('/directoryConnector/domain')
        except CTERAException:
            pass
        return domain

    def domains(self):
        """
        Get domains

        :return list(str): List of names of all discovered domains
        """
        return self._core.api.execute('', 'getADTrustedDomains', False)

    def fetch(self, active_directory_accounts):
        """
        Instruct the Portal to fetch the provided Active Directory Accounts

        :param list[cterasdk.core.types.PortalAccount] active_directory_accounts: List of Active Directory Accounts to fetch

        :return: Response Code
        """
        domains = self._core.domains.list_domains()
        account_types = [v for k, v in PortalAccountType.__dict__.items() if not k.startswith('_')]

        param = []
        for active_directory_account in active_directory_accounts:
            if active_directory_account.directory not in domains:
                logging.getLogger('cterasdk.core').error('Invalid domain name. %s', {'domain': active_directory_account.directory})
                raise CTERAException('Invalid domain', None, domain=active_directory_account.directory, domains=domains)

            if active_directory_account.account_type not in account_types:
                logging.getLogger('cterasdk.core').error('Invalid account type. %s', {'type': active_directory_account.account_type})
                raise CTERAException('Invalid account type', None, type=active_directory_account.account_type, options=account_types)

        for active_directory_account in active_directory_accounts:
            if active_directory_account.account_type == PortalAccountType.User:
                param.append(self._search_users(active_directory_account.directory, active_directory_account.name))
            elif active_directory_account.account_type == PortalAccountType.Group:
                param.append(self._search_groups(active_directory_account.directory, active_directory_account.name))

        logging.getLogger('cterasdk.core').info('Starting to fetch users and groups.')
        response = self._core.api.execute('', 'syncAD', param)
        logging.getLogger('cterasdk.core').info('Started fetching users and groups.')

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

        logging.getLogger('cterasdk.core').info(
            'Searching %(search_type)s: %(info)s',
            dict(search_type=search_type, info={'domain': domain, 'name': name})
        )

        objects = self._core.api.execute('', 'searchAD', param)
        if not objects:
            logging.getLogger('cterasdk.core').info('Could not find results that match your search criteria. %s',
                                                    {'domain': domain, 'name': name})
            raise CTERAException(
                'Could not find results that match your search criteria',
                None,
                domain=domain,
                type=search_type,
                account=name
            )

        for principal in objects:
            if principal.name == name:
                logging.getLogger('cterasdk.core').info('Found. %s', {'domain': domain, 'name': name})
                return principal

        raise CTERAException(
            'Search returned multiple results, but none matched your search criteria',
            None,
            domain=domain,
            type=search_type,
            account=name
        )

    def disconnect(self):
        """
        Disconnect a Portal tenant from directory services
        """
        return self._core.api.put('/directoryConnector', None)
