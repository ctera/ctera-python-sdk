import logging

from .common import SrcDstParam, ActionResourcesParam

def rename(ctera_host, path, name):
    
    rename_param = ActionResourcesParam.instance()

    param = SrcDstParam.instance(src = path.fullpath(), dest = path.parent().joinpath(name).fullpath())

    rename_param.add(param)
    
    logging.getLogger().info('Renaming item. {0}'.format({'path' : str(path.relativepath), 'name' : name}))
    
    return ctera_host.execute('', 'moveResources', rename_param)