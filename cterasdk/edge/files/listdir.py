import logging

from ...common import Object


def ls(CTERAHost, path):
    param = Object()
    param.path = path
    logging.getLogger().debug('Listing directory. %s', {'path': param.path})
    return CTERAHost.execute('/status/fileManager', 'listPhysicalFolders', param)