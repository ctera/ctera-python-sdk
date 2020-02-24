import logging

from ... import config
from ...lib import FileSystem
from .open import openfile
from ...exception import LocalDirectoryNotFound


def download(ctera_host, path):
    dirpath = config.filesystem['dl']
    handle = openfile(ctera_host, path)
    try:
        FileSystem.instance().save(dirpath, path.name(), handle)
    except LocalDirectoryNotFound as error:
        dirpath = FileSystem.instance().expanduser(dirpath)
        logging.getLogger().error('Download failed. Check the following directory exists. %s', {'path': dirpath})
        if handle is not None:
            handle.close()
        raise error
