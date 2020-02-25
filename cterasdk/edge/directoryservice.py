import logging

from ..common import Object
from ..exception import CTERAException, CTERAConnectionError
from .base_command import BaseCommand


class DirectoryService(BaseCommand):

    def connect(self, domain, username, password, ou=None):
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
        mappings = self._gateway.get('/config/fileservices/cifs/idMapping/map')
        for mapping in mappings:
            if domain == mapping.domainFlatName:
                mapping.minID = start
                mapping.maxID = end
                logging.getLogger().debug('Configuring advanced mapping. %s', {'domain': domain, 'start': start, 'end': end})
                return self._gateway.put('/config/fileservices/cifs/idMapping/map', mappings)

        logging.getLogger().error('Could not find domain name. %s', {'domain': domain})
        raise CTERAException('Could not find domain name', None, domain=domain, domains=self.domains())

    def domains(self):
        return [domain.flatName for domain in self._gateway.execute('/status/fileservices/cifs', 'enumDiscoveredDomains')]

    def disconnect(self):
        logging.getLogger().info("Disconnecting from Active Directory.")

        cifs = self._gateway.get('/config/fileservices/cifs')
        cifs.type = "workgroup"
        cifs.workgroup = "CTERA"
        cifs.domain = None

        self._gateway.put('/config/fileservices/cifs', cifs)
        logging.getLogger().info("Disconnected from Active Directory.")
