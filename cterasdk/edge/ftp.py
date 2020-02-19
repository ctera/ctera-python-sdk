from .enum import Mode

import logging
    
def disable(ctera_host):
    
    logging.getLogger().info('Disabling FTP server.')
    
    ctera_host.put('/config/fileservices/ftp/mode', Mode.Disabled)
    
    logging.getLogger().info('FTP server disabled.')