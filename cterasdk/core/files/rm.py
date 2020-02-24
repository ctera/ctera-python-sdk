import logging

from .common import SrcDstParam, ActionResourcesParam


def delete(ctera_host, path):
    return delete_multi(ctera_host, *[path])


def delete_multi(ctera_host, *paths):
    delete_param = ActionResourcesParam.instance()

    for path in paths:
        logging.getLogger().info('Deleting item. %s', {'path': str(path.relativepath)})
        delete_param.add(SrcDstParam.instance(src=path.fullpath()))

    return ctera_host.execute('', 'deleteResources', delete_param)
