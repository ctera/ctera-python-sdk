import logging

def location(ctera_host):
    
    return ctera_host.get('/config/device/location')

def set_location(ctera_host, location):
    
    logging.getLogger().info('Configuring device location. {0}'.format({'location' : location}))
    
    return ctera_host.put('/config/device/location', location)

def hostname(ctera_host):
    
    return ctera_host.get('/config/device/hostname')

def set_hostname(ctera_host, hostname):
    
    logging.getLogger().info('Configuring device hostname. {0}'.format({'hostname' : hostname}))
    
    return ctera_host.put('/config/device/hostname', hostname)