import logging


def openfile(ctera_host, path):
    fullpath = path.fullpath()
    logging.getLogger().info('Obtaining file handle. %s', {'path': fullpath})
    return ctera_host.openfile(ctera_host._files(), fullpath, params={})  # pylint: disable=protected-access
