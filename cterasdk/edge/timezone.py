import logging

from .enum import Mode

def set_timezone(ctera_host, timezone):
    
    logging.getLogger().info("Updating timezone. {0}".format({'timezone' : timezone}))
    
    ctera_host.put('/config/time/TimeZone', timezone)
    
    logging.getLogger().info("Timezone updated. {0}".format({'timezone' : timezone}))