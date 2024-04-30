import atexit
import logging
import shutil
import tempfile

from .registry import Registry


class TempfileServices:

    __tempdir_prefix = 'cterasdk-'

    @staticmethod
    def mkdir():
        registry = Registry.instance()
        tempdir = registry.get('tempdir')
        if tempdir is None:
            logging.getLogger('cterasdk.filesystem').debug('Creating temporary directory.')
            tempdir = tempfile.mkdtemp(prefix=TempfileServices.__tempdir_prefix)
            logging.getLogger('cterasdk.filesystem').debug('Temporary directory created. %s', {'path': tempdir})
            registry.register('tempdir', tempdir)
        return tempdir

    @staticmethod
    def mkfile(prefix, suffix):
        tempdir = TempfileServices.mkdir()
        logging.getLogger('cterasdk.filesystem').debug('Creating temporary file.')
        fd, filepath = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=tempdir)
        logging.getLogger('cterasdk.filesystem').debug('Temporary file created. %s', {'path': filepath})
        return (fd, filepath)

    @staticmethod
    @atexit.register
    def rmdir():
        registry = Registry.instance()
        tempdir = registry.get('tempdir')
        if tempdir is not None:
            logging.getLogger('cterasdk.filesystem').debug('Removing temporary directory. %s', {'path': tempdir})
            shutil.rmtree(path=tempdir)
            logging.getLogger('cterasdk.filesystem').debug('Removed temporary directory. %s', {'path': tempdir})
            registry.remove('tempdir')
