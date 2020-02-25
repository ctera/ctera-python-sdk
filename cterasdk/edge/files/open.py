import logging


def openfile(ctera_host, path):
    fullpath = path.fullpath()
    logging.getLogger().info('Obtaining file handle. %s', {'path': fullpath})
    return ctera_host.openfile(fullpath, use_file_url=True)
