import logging

from .network import tcp_connect
from ..common import Object
from ..exception import CTERAException, CTERAConnectionError


def connect(ctera_host, domain, username, password, ou):
    host = ctera_host.host()
    port = 389
    tcp_conn_status = tcp_connect(ctera_host, address=domain, port=port)

    if not tcp_conn_status:
        logging.getLogger().error("Connection failed. No traffic allowed over port %(port)s", dict(port=port))
        raise CTERAConnectionError('Unable to establish connection', None, host=host, port=port, protocol='LDAP')

    cifs = ctera_host.get('/config/fileservices/cifs')
    cifs.type = "domain"
    cifs.domain = domain
    cifs.workgroup = None
    ctera_host.put('/config/fileservices/cifs', cifs)

    param = Object()
    param.username = username
    param.password = password
    if ou is not None:
        param.ouPath = ou

    logging.getLogger().info("Connecting to Active Directory. %s", {'domain': domain, 'user': username})

    try:
        ctera_host.execute("/status/fileservices/cifs", "joinDomain", param)
    except CTERAException as error:
        logging.getLogger().error("Failed connecting to Active Directory.")
        raise error

    logging.getLogger().info("Connected to Active Directory.")


def advanced_mapping(ctera_host, domain, start, end):
    mappings = ctera_host.get('/config/fileservices/cifs/idMapping/map')
    for mapping in mappings:
        if domain == mapping.domainFlatName:
            mapping.minID = start
            mapping.maxID = end
            logging.getLogger().debug('Configuring advanced mapping. %s', {'domain': domain, 'start': start, 'end': end})
            return ctera_host.put('/config/fileservices/cifs/idMapping/map', mappings)

    logging.getLogger().error('Could not find domain name. %s', {'domain': domain})
    raise CTERAException('Could not find domain name', None, domain=domain, domains=domains(ctera_host))


def domains(ctera_host):
    return [domain.flatName for domain in ctera_host.execute('/status/fileservices/cifs', 'enumDiscoveredDomains')]


def disconnect(ctera_host):
    logging.getLogger().info("Disconnecting from Active Directory.")

    cifs = ctera_host.get('/config/fileservices/cifs')
    cifs.type = "workgroup"
    cifs.workgroup = "CTERA"
    cifs.domain = None

    ctera_host.put('/config/fileservices/cifs', cifs)
    logging.getLogger().info("Disconnected from Active Directory.")
