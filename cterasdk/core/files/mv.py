import logging

from .common import SrcDstParam, ActionResourcesParam

def move(ctera_host, src, dest):
    
    return move_multi(ctera_host, [src], dest)

def move_multi(ctera_host, src, dest):
    
    move_param = ActionResourcesParam.instance()
    
    for path in src:
        
        logging.getLogger().info('Moving item. {0}'.format({'path' : str(path.relativepath), 'to' : str(dest.relativepath)}))
        
        param = SrcDstParam.instance(src = path.fullpath(), dest = dest.joinpath(path.name()).fullpath())
        
        move_param.add(param)
        
    return ctera_host.execute('', 'moveResources', move_param)