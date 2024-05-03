import re
import logging

from ..common import Object
from ..exceptions import CTERAException
from .base_command import BaseCommand
from .types import TCPService


class DirectoryService(BaseCommand):
    """
    Edge Filer Active Directory configuration APIs
    """

    def connected(self):
        """
        Get the Active Directory join status
        """
        return self._edge.api.get('/status/fileservices/cifs/joinStatus') == 0

    def connect(self, domain, username, password, ou=None, check_connection=False):
        """
        Connect the Edge Filer to an Active Directory

        :param str domain: The active directory domain to connect to
        :param str username: The user name to use when connecting to the active directory services
        :param str password: The password to use when connecting to the active directory services
        :param str,optional ou: The OU path to use when connecting to the active directory services, defaults to None
        :param bool,optional check_connection: Check connectivity before attempting to connect to directory services, defaults to `False`
        """
        if check_connection:
            self._check_domain_connectivity(domain)

        cifs = self._edge.api.get('/config/fileservices/cifs')
        cifs.type = "domain"
        cifs.domain = domain
        cifs.workgroup = None
        self._edge.api.put('/config/fileservices/cifs', cifs)

        param = Object()
        param.username = username
        param.password = password
        if ou is not None:
            param.ouPath = ou
        logging.getLogger('cterasdk.edge').info("Connecting to Active Directory. %s", {'domain': domain, 'user': username})

        try:
            self._edge.api.execute("/status/fileservices/cifs", "joinDomain", param)
        except CTERAException as error:
            logging.getLogger('cterasdk.edge').error("Failed connecting to Active Directory.")
            raise error
        logging.getLogger('cterasdk.edge').info("Connected to Active Directory.")

    def _check_domain_connectivity(self, domain):
        port = 389
        domain_controllers = self.get_static_domain_controller()
        domain_controllers = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', domain_controllers) if domain_controllers else [domain]
        connection_results = self._edge.network.diagnose([TCPService(host, port) for host in domain_controllers])
        for connection_result in connection_results:
            if not connection_result.is_open:
                logging.getLogger('cterasdk.edge').error("Connection failed. No traffic allowed over port %(port)s",
                                                         dict(port=connection_result.port))
                raise ConnectionError(f'Unable to establish LDAP connection {connection_result.host}:{connection_result.port}')

    def get_static_domain_controller(self):
        """
        Retrieve the static domain controller configuration

        :return: A FQDN, hostname or ip address of the domain controller
        :rtype: str
        """
        return self._edge.api.get('/config/fileservices/cifs/passwordServer')

    def set_static_domain_controller(self, dc):
        """
        Configure the Edge Filer to use a static domain controller

        :param str dc: The FQDN, hostname or ip address of the domain controller
        :return: The FQDN, hostname or ip address of the domain controller
        :rtype: str
        """
        return self._edge.api.put('/config/fileservices/cifs/passwordServer', dc)

    def remove_static_domain_controller(self):
        """
        Delete the static domain controller configuration
        """
        self._edge.api.put('/config/fileservices/cifs/passwordServer', None)

    def get_advanced_mapping(self):
        """
        Retrieve directory services advanced mapping configuration

        :returns: A dictionary of domain mapping objects
        :rtype: dict
        """
        return {mapping.domainFlatName: mapping for mapping in self._edge.api.get('/config/fileservices/cifs/idMapping/map')}

    def set_advanced_mapping(self, mappings):
        """
        Configure advanced mapping

        :param list[cterasdk.common.types.ADDomainIDMapping] mappings: List of domains and their UID/GID mapping range
        """
        if not self.connected():
            raise CTERAException('Failed to configure advanced mapping. Not connected to directory services.')

        domains = self.domains()
        advanced_mapping = self._edge.api.get('/config/fileservices/cifs/idMapping/map')
        advanced_mapping = []
        for mapping in mappings:
            if mapping.domainFlatName in domains:
                advanced_mapping.append(mapping)
            else:
                logging.getLogger('cterasdk.edge').warning('Invalid mapping. Could not find domain. %s', {'domain': mapping.domainFlatName})

        logging.getLogger('cterasdk.edge').debug('Updating advanced mapping. %s', {
            'domains': [mapping.domainFlatName for mapping in advanced_mapping]
        })
        response = self._edge.api.put('/config/fileservices/cifs/idMapping/map', advanced_mapping)
        logging.getLogger('cterasdk.edge').info('Updated advanced mapping.')

        return response

    def get_connected_domain(self):
        """
        Get the connected domain information

        :return cterasdk.common.object.Object:
        """
        cifs = self._edge.api.get('/config/fileservices/cifs')
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
        return [domain.flatName for domain in self._edge.api.execute('/status/fileservices/cifs', 'enumDiscoveredDomains')]

    def disconnect(self):
        """
        Disconnect from Active Directory Service
        """
        logging.getLogger('cterasdk.edge').info("Disconnecting from Active Directory.")

        cifs = self._edge.api.get('/config/fileservices/cifs')
        cifs.type = "workgroup"
        cifs.workgroup = "CTERA"
        cifs.domain = None

        self._edge.api.put('/config/fileservices/cifs', cifs)
        logging.getLogger('cterasdk.edge').info("Disconnected from Active Directory.")
