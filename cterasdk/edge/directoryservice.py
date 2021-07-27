import re
import logging

from ..common import Object
from ..exception import CTERAException, CTERAConnectionError
from .base_command import BaseCommand
from .types import TCPService


class DirectoryService(BaseCommand):
    """
    Gateway Active Directory configuration APIs
    """

    def connected(self):
        """
        Get the Active Directory join status
        """
        return self._gateway.get('/status/fileservices/cifs/joinStatus') == 0

    def connect(self, domain, username, password, ou=None, check_connection=False):
        """
        Connect the Gateway to an Active Directory

        :param str domain: The active directory domain to connect to
        :param str username: The user name to use when connecting to the active directory services
        :param str password: The password to use when connecting to the active directory services
        :param str,optional ou: The OU path to use when connecting to the active directory services, defaults to None
        :param bool,optional check_connection: Check connectivity before attempting to connect to directory services, defaults to `False`
        """
        if check_connection:
            self._check_domain_connectivity(domain)

        cifs = self._gateway.get('/config/fileservices/cifs')
        cifs.type = "domain"
        cifs.domain = domain
        cifs.workgroup = None
        self._gateway.put('/config/fileservices/cifs', cifs)

        param = Object()
        param.username = username
        param.password = password
        if ou is not None:
            param.ouPath = ou
        logging.getLogger().info("Connecting to Active Directory. %s", {'domain': domain, 'user': username})

        try:
            self._gateway.execute("/status/fileservices/cifs", "joinDomain", param)
        except CTERAException as error:
            logging.getLogger().error("Failed connecting to Active Directory.")
            raise error
        logging.getLogger().info("Connected to Active Directory.")

    def _check_domain_connectivity(self, domain):
        port = 389
        domain_controllers = self.get_static_domain_controller()
        domain_controllers = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', domain_controllers) if domain_controllers else [domain]
        connection_results = self._gateway.network.diagnose([TCPService(host, port) for host in domain_controllers])
        for connection_result in connection_results:
            if not connection_result.is_open:
                logging.getLogger().error("Connection failed. No traffic allowed over port %(port)s", dict(port=connection_result.port))
                raise CTERAConnectionError('Unable to establish connection', None, host=connection_result.host,
                                           port=connection_result.port, protocol='LDAP')

    def get_static_domain_controller(self):
        """
        Retrieve the static domain controller configuration

        :return: A FQDN, hostname or ip address of the domain controller
        :rtype: str
        """
        return self._gateway.get('/config/fileservices/cifs/passwordServer')

    def set_static_domain_controller(self, dc):
        """
        Configure the Gateway to use a static domain controller

        :param str dc: The FQDN, hostname or ip address of the domain controller
        :return: The FQDN, hostname or ip address of the domain controller
        :rtype: str
        """
        return self._gateway.put('/config/fileservices/cifs/passwordServer', dc)

    def remove_static_domain_controller(self):
        """
        Delete the static domain controller configuration
        """
        self._gateway.put('/config/fileservices/cifs/passwordServer', None)

    def advanced_mapping(self, domain, start, end):
        """
        Configure advanced mapping

        :param str domain: The active directory domain
        :param int start: The minimum id to use for mapping
        :param int end: The maximum id to use for mapping
        """
        mappings = self._gateway.get('/config/fileservices/cifs/idMapping/map')
        for mapping in mappings:
            if domain == mapping.domainFlatName:
                mapping.minID = start
                mapping.maxID = end
                logging.getLogger().debug('Configuring advanced mapping. %s', {'domain': domain, 'start': start, 'end': end})
                return self._gateway.put('/config/fileservices/cifs/idMapping/map', mappings)

        logging.getLogger().error('Could not find domain name. %s', {'domain': domain})
        raise CTERAException('Could not find domain name', None, domain=domain, domains=self.domains())

    def get_connected_domain(self):
        """
        Get the connected domain information

        :return cterasdk.common.object.Object:
        """
        cifs = self._gateway.get('/config/fileservices/cifs')
        obj = Object()
        obj.type = cifs.type
        obj.domain = cifs.domain
        obj.workgroup = cifs.workgroup
        return obj

    def domains(self):
        """
        Get all domains

        :return list(str): List of names of all discovered domains
        """
        return [domain.flatName for domain in self._gateway.execute('/status/fileservices/cifs', 'enumDiscoveredDomains')]

    def disconnect(self):
        """
        Disconnect from Active Directory Service
        """
        logging.getLogger().info("Disconnecting from Active Directory.")

        cifs = self._gateway.get('/config/fileservices/cifs')
        cifs.type = "workgroup"
        cifs.workgroup = "CTERA"
        cifs.domain = None

        self._gateway.put('/config/fileservices/cifs', cifs)
        logging.getLogger().info("Disconnected from Active Directory.")
