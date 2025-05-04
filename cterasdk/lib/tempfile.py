import atexit
import logging
import shutil
import tempfile

from .registry import Registry


logger = logging.getLogger('cterasdk.filesystem')


class TempfileServices:

    __tempdir_prefix = 'cterasdk-'

    @staticmethod
    def mkdir():
        registry = Registry.instance()
        tempdir = registry.get('tempdir')
        if tempdir is None:
            logger.debug('Creating temporary directory.')
            tempdir = tempfile.mkdtemp(prefix=TempfileServices.__tempdir_prefix)
            logger.debug('Temporary directory created. %s', {'path': tempdir})
            registry.register('tempdir', tempdir)
        return tempdir

    @staticmethod
    def mkfile(prefix, suffix):
        tempdir = TempfileServices.mkdir()
        logger.debug('Creating temporary file.')
        fd, filepath = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=tempdir)
        logger.debug('Temporary file created. %s', {'path': filepath})
        return (fd, filepath)

    @staticmethod
    @atexit.register
    def rmdir():
        registry = Registry.instance()
        tempdir = registry.get('tempdir')
        if tempdir is not None:
            logger.debug('Removing temporary directory. %s', {'path': tempdir})
            shutil.rmtree(path=tempdir)
            logger.debug('Removed temporary directory. %s', {'path': tempdir})
            registry.remove('tempdir')
