from ...lib import Iterator, Command
from .fetch_resources_param import FetchResourcesParamBuilder


def list_dir(ctera_host, param):
    response = fetch_resources(ctera_host, param)
    return (response.hasMore, response.items)


def fetch_resources(ctera_host, param):
    return ctera_host.execute('', 'fetchResources', param)


def ls(ctera_host, path, depth=1):
    param = FetchResourcesParamBuilder().root(path.encoded_fullpath()).depth(depth).build()
    if depth > 0:
        function = Command(list_dir, ctera_host)
        return Iterator(function, param)
    return fetch_resources(ctera_host, param)
