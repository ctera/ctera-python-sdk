import logging

from .common import SrcDstParam, ActionResourcesParam

def delete(ctera_host, path):
    
    return delete_multi(ctera_host, *[path])

def delete_multi(ctera_host, *paths):
    
    delete_param = ActionResourcesParam.instance()
    
    for path in paths:
        
        logging.getLogger().info('Deleting item. {0}'.format({'path' : str(path.relativepath)}))
        
        param = SrcDstParam.instance(src = path.fullpath())
        
        delete_param.add(param)
    
    return ctera_host.execute('', 'deleteResources', delete_param)