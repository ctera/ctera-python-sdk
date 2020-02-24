import logging

from .common import SrcDstParam, ActionResourcesParam


def rename(ctera_host, path, name):
    rename_param = ActionResourcesParam.instance()
    rename_param.add(SrcDstParam.instance(src=path.fullpath(), dest=path.parent().joinpath(name).fullpath()))

    logging.getLogger().info('Renaming item. %s', {'path': str(path.relativepath), 'name': name})

    return ctera_host.execute('', 'moveResources', rename_param)
