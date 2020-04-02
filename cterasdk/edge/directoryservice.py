import logging

from ..common import Object
from ..exception import CTERAException, CTERAConnectionError
from .base_command import BaseCommand


class DirectoryService(BaseCommand):
    """
    Gateway Active Directory configuration APIs
    """

    def connect(self, domain, username, password, ou=None):
        """
        Connect the Gateway to an Active Directory

        :param str domain: The active directory domain to connect to
        :param str username: The user name to use when connecting to the active directory services
        :param str password: The password to use when connecting to the active directory services
        :param str,optional ou: The OU path to use when connecting to the active directory services, defaults to None
        """
        host = self._gateway.host()
        port = 389
        tcp_conn_status = self._gateway.network.tcp_connect(address=domain, port=port)
        if not tcp_conn_status:
            logging.getLogger().error("Connection failed. No traffic allowed over port %(port)s", dict(port=port))
            raise CTERAConnectionError('Unable to establish connection', None, host=host, port=port, protocol='LDAP')

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

    def advanced_mapping(self, domain, start, end):
        """
        Configure advanced mapping

        :param str domain: The active directory domain
        :param str start: The minimum id to use for mapping
        :param str end: The maximum id to use for mapping
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
