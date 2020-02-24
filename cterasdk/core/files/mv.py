import logging

from .common import SrcDstParam, ActionResourcesParam


def move(ctera_host, src, dest):
    return move_multi(ctera_host, [src], dest)


def move_multi(ctera_host, src, dest):
    move_param = ActionResourcesParam.instance()

    for path in src:
        logging.getLogger().info('Moving item. %s', {'path': str(path.relativepath), 'to': str(dest.relativepath)})
        move_param.add(SrcDstParam.instance(src=path.fullpath(), dest=dest.joinpath(path.name()).fullpath()))

    return ctera_host.execute('', 'moveResources', move_param)
