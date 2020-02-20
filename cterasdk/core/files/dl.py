import logging

from ... import config
from ...lib import FileSystem
from ...exception import LocalDirectoryNotFound
from ...core.files.open import openfile

def download(ctera_host, path, save_as):
    dirpath = config.filesystem['dl']
    handle = openfile(ctera_host, path)
    try:
        FileSystem.instance().save(dirpath, save_as, handle)
    except LocalDirectoryNotFound as error:
        dirpath = FileSystem.instance().expanduser(dirpath)
        logging.getLogger().error('Download failed. Check the following directory exists. %s', {'path' : dirpath})
        if handle is not None:
            handle.close()
        raise error
