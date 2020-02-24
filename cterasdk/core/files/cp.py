import logging

from .common import SrcDstParam, ActionResourcesParam


def copy(ctera_host, src, dest):
    return copy_multi(ctera_host, [src], dest)


def copy_multi(ctera_host, src, dest):
    copy_param = ActionResourcesParam.instance()

    for path in src:
        logging.getLogger().info('Copying item. %s', {'path': str(path.relativepath), 'to': str(dest.relativepath)})

        param = SrcDstParam.instance(src=path.fullpath(), dest=dest.joinpath(path.name()).fullpath())
        copy_param.add(param)

    return ctera_host.execute('', 'copyResources', copy_param)
