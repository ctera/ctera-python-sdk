"""

"""
import logging

from cterasdk import config
from cterasdk.lib import FileSystem
from cterasdk.exception import LocalDirectoryNotFound
from cterasdk.core.files.open import openfile

def download(ctera_host, path, save_as):
    dirpath = config.filesystem['dl']
    handle = openfile(ctera_host, path)
    try:
        FileSystem.instance().save(dirpath, save_as, handle)
    except LocalDirectoryNotFound as error:
        dirpath = FileSystem.instance().expanduser(dirpath)
        logging.getLogger().error('Download failed. Check the following directory exists. {0}'.format({'path' : dirpath}))
        if handle != None:
            handle.close()
        raise error
