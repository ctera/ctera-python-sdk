import logging
from . import common


def listdir(core, path, depth=None, include_deleted=False):
    depth = depth if depth is not None else 1
    builder = common.FetchResourcesParamBuilder().root(path.encoded_fullpath()).depth(depth)
    if include_deleted:
        builder.include_deleted()
    param = builder.build()
    if depth > 0:
        return common.objects_iterator(core, param)
    return common.fetch_resources(core, param)


def walk(core, base, path, include_deleted=False):
    paths = [common.get_object_path(base, path)]
    while len(paths) > 0:
        path = paths.pop(0)
        elements = listdir(core, path, include_deleted=include_deleted)
        for element in elements:
            if element.isFolder:
                paths.append(common.get_object_path(base, element))
            yield element


def mkdir(core, path):
    param = common.get_create_dir_param(path.name(), path.parent().encoded_fullpath())
    logging.getLogger('cterasdk.core').info('Creating directory. %s', {'path': str(path.relative)})
    response = core.api.execute('', 'makeCollection', param)
    common.raise_for_status(response, str(path.relative))
    logging.getLogger('cterasdk.core').info('Directory created. %s', {'path': str(path.relative)})


def makedirs(core, path):
    directories = path.parts()
    for i in range(1, len(directories) + 1):
        path = common.get_object_path(path.base, '/'.join(directories[:i]))
        try:
            mkdir(core, path)
        except common.ItemExists:
            pass


def rename(core, path, name):
    param = common.ActionResourcesParam.instance()
    logging.getLogger('cterasdk.core').info('Renaming item. %s', {'path': str(path.relative), 'name': name})
    param.add(common.SrcDstParam.instance(src=path.fullpath(), dest=path.parent().joinpath(name).fullpath()))
    return core.api.execute('', 'moveResources', param)


def remove(core, *paths):
    param = common.ActionResourcesParam.instance()
    paths = [paths] if not isinstance(paths, tuple) else paths
    for path in paths:
        logging.getLogger('cterasdk.core').info('Deleting item. %s', {'path': str(path.relative)})
        param.add(common.SrcDstParam.instance(src=path.fullpath()))
    return core.api.execute('', 'deleteResources', param)


def recover(core, *paths):
    param = common.ActionResourcesParam.instance()
    paths = [paths] if not isinstance(paths, tuple) else paths
    for path in paths:
        logging.getLogger('cterasdk.core').info('Recovering item. %s', {'path': str(path.relative)})
        param.add(common.SrcDstParam.instance(src=path.fullpath()))
    return core.api.execute('', 'restoreResources', param)


def copy(core, *paths, destination=None):
    param = common.ActionResourcesParam.instance()
    paths = [paths] if not isinstance(paths, tuple) else paths
    for path in paths:
        logging.getLogger('cterasdk.core').info('Copying item. %s', {'path': str(path.relative), 'to': str(destination.relative)})
        param.add(common.SrcDstParam.instance(src=path.fullpath(), dest=destination.joinpath(path.name()).fullpath()))
    return core.api.execute('', 'copyResources', param)


def move(core, *paths, destination=None):
    param = common.ActionResourcesParam.instance()
    paths = [paths] if not isinstance(paths, tuple) else paths
    for path in paths:
        logging.getLogger('cterasdk.core').info('Copying item. %s', {'path': str(path.relative), 'to': str(destination.relative)})
        param.add(common.SrcDstParam.instance(src=path.fullpath(), dest=destination.joinpath(path.name()).fullpath()))
    return core.api.execute('', 'moveResources', param)
