from . import session

from ..exception import CTERAException

from ..convert.exception import ParseException

import logging

def remote_access(Gateway, Portal):
    
    tenant = Portal.session().tenant()
    
    device = Gateway.host()
    
    logging.getLogger().info("Enabling remote access. {0}".format({'tenant' : tenant, 'device' : device}))
    
    ticket = obtain_ticket(Portal, device)
    
    Gateway.session().enable_remote_access()
    
    login(Gateway, ticket)
    
    logging.getLogger().info("Enabled remote access. {0}".format({'tenant' : tenant, 'device' : device}))
    
def login(Gateway, ticket):
        
    logging.getLogger().debug("Logging in using SSO ticket. {0}".format({'device' : Gateway.host()}))

    Gateway.get('/ssologin', { 'ticket' : ticket })
    
def obtain_ticket(Portal, device_name):
    
    tenant = Portal.session().tenant()
    
    url = '/portals/%s/devices/%s' % (tenant, device_name)
    
    logging.getLogger().debug("Obtaining SSO ticket. {0}".format({'tenant' : tenant, 'device' : device_name}))
    
    ticket = Portal.execute(url, 'singleSignOn')
    
    if not ticket:
        
        logging.getLogger().error('Could not obtain SSO ticket. {0}'.format({'tenant' : tenant, 'device' : device_name}))
        
        raise CTERAException('Could not obtain SSO ticket.')
        
    else:
        
        logging.getLogger().debug("Obtained SSO ticket. {0}".format({'tenant' : tenant, 'device' : device_name}))
        
        return ticket