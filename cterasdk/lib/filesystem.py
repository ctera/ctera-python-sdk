import logging
import os

from ..exception import RenameException, LocalDirectoryNotFound


class FileSystem:

    __instance = None

    @staticmethod
    def instance():
        if FileSystem.__instance is None:
            FileSystem()
        return FileSystem.__instance

    def __init__(self):
        if FileSystem.__instance is not None:
            raise Exception("FileSystem is a singleton class.")
        FileSystem.__instance = self

    @staticmethod
    def expanduser(path):
        return os.path.expanduser(path)

    @staticmethod
    def exists(filepath):
        return os.path.exists(filepath)

    def rename(self, dirpath, src, dst):
        source = os.path.join(dirpath, src)
        if self.exists(source):
            destination = os.path.join(dirpath, dst)
            os.rename(source, destination)
            return (dirpath, dst)
        logging.getLogger().error('Could not rename temporary file. File not found. %s', {'path' : dirpath, 'temp' : src})
        raise RenameException(dirpath, src, dst)

    def save(self, dirpath, filename, handle):
        dirpath = os.path.expanduser(dirpath)
        if not self.exists(dirpath):
            raise LocalDirectoryNotFound(dirpath)

        tempfile = filename + '.Chopin3'
        filepath = os.path.join(dirpath, tempfile)
        self.write(filepath, handle)
        origin = filename
        version = 0
        while True:
            try:
                dirpath, filename = self.rename(dirpath, tempfile, filename)
                logging.getLogger().debug('Renamed temporary file. %s', {'path' : dirpath, 'temp' : tempfile, 'name' : filename})
                break
            except (FileExistsError, IsADirectoryError):
                logging.getLogger().debug('File exists. %s', {'path' : dirpath, 'name' : filename})
                version = version + 1
                filename = self.version(origin, version)

        filepath = os.path.join(dirpath, filename)
        logging.getLogger().info('Saved. %s', {'path' : filepath})
        return filepath

    @staticmethod
    def version(filename, version):
        idx = filename.rfind('.')
        extension = ''
        if idx > 0:
            name = filename[:idx]
            extension = filename[idx:]
        else:
            name = filename
        return name + ' ' + '(' + str(version) + ')' + extension

    @staticmethod
    def write(filepath, handle):
        sizeof = 8192
        f = None
        try:
            f = open(filepath, 'w+b')
            while True:
                buffer = handle.read(sizeof)
                if not buffer:
                    break
                f.write(buffer)
        except OSError:
            # TODO pylint: disable=fixme
            pass
        finally:
            if f is not None:
                f.close()
                logging.getLogger().debug('Saved temporary file. %s', {'path' : filepath})
            if handle is not None:
                handle.close()
