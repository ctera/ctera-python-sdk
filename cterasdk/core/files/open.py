import logging


def openfile(ctera_host, path):
    logging.getLogger().info('Obtaining file handle. %s', {'path' : str(path.relativepath)})
    return ctera_host.openfile(ctera_host.baseurl(), path.fullpath(), params={})
