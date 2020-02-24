import logging

from .common import SrcDstParam, ActionResourcesParam


def undelete(ctera_host, path):
    return undelete_multi(ctera_host, *[path])


def undelete_multi(ctera_host, *paths):
    undelete_param = ActionResourcesParam.instance()
    for path in paths:
        logging.getLogger().info('Recovering item. %s', {'path': str(path.relativepath)})
        undelete_param.add(SrcDstParam.instance(src=path.fullpath()))

    return ctera_host.execute('', 'restoreResources', undelete_param)
