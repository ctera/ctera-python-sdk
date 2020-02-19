import logging

def delete(ctera_host, path):
    
    fullpath = path.fullpath()
    
    logging.getLogger().info('Deleting item. {0}'.format({'path' : fullpath}))
    
    response = ctera_host.rm(fullpath)
    
    logging.getLogger().info('Item deleted. {0}'.format({'path' : fullpath}))
    
    return response