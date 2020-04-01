from ...lib import Iterator, Command
from .fetch_resources_param import FetchResourcesParamBuilder


def list_dir(ctera_host, param):
    response = ctera_host.execute('', 'fetchResources', param)
    return (response.hasMore, response.items)


def ls(ctera_host, path):
    param = FetchResourcesParamBuilder().root(path.encoded_fullpath()).depth(1).build()
    function = Command(list_dir, ctera_host)
    return Iterator(function, param)
