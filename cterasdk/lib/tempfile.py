import atexit
import logging
import shutil
import tempfile

from .registry import Registry


class TempfileServices:

    __tempdir_prefix = 'chopin_core-'

    @staticmethod
    def mkdir():
        registry = Registry.instance()
        tempdir = registry.get('tempdir')
        if tempdir is None:
            logging.getLogger().debug('Creating temporary directory.')
            tempdir = tempfile.mkdtemp(prefix=TempfileServices.__tempdir_prefix)
            logging.getLogger().debug('Temporary directory created. %s', {'path': tempdir})
            registry.register('tempdir', tempdir)
        return tempdir

    @staticmethod
    def mkfile(prefix, suffix):
        tempdir = TempfileServices.mkdir()
        logging.getLogger().debug('Creating temporary file.')
        fd, filepath = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=tempdir)
        logging.getLogger().debug('Temporary file created. %s', {'path': filepath})
        return (fd, filepath)

    @staticmethod
    @atexit.register
    def rmdir():
        registry = Registry.instance()
        tempdir = registry.get('tempdir')
        if tempdir is not None:
            logging.getLogger().debug('Removing temporary directory. %s', {'path': tempdir})
            shutil.rmtree(path=tempdir)
            logging.getLogger().debug('Removed temporary directory. %s', {'path': tempdir})
            registry.remove('tempdir')
