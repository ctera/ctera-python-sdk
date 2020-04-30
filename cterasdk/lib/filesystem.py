import logging
import mimetypes
import os
from pathlib import Path

from .. import config
from ..exception import RenameException, LocalDirectoryNotFound, LocalFileNotFound, LocalPathNotFound


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
        logging.getLogger().error('Could not rename temporary file. File not found. %s', {'path': dirpath, 'temp': src})
        raise RenameException(dirpath, src, dst)

    def validate_directory(self, dirpath):
        dirpath = os.path.expanduser(dirpath)
        if not self.exists(dirpath):
            raise LocalDirectoryNotFound(dirpath)

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
                logging.getLogger().debug('Renamed temporary file. %s', {'path': dirpath, 'temp': tempfile, 'name': filename})
                break
            except (FileExistsError, IsADirectoryError):
                logging.getLogger().debug('File exists. %s', {'path': dirpath, 'name': filename})
                version = version + 1
                filename = self.version(origin, version)

        filepath = os.path.join(dirpath, filename)
        logging.getLogger().info('Saved. %s', {'path': filepath})
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
        with open(filepath, 'w+b') as fd:
            for chunk in handle.iter_content(chunk_size=8192):
                fd.write(chunk)
        logging.getLogger().debug('Saved temporary file. %s', {'path': filepath})

    @staticmethod
    def get_local_file_info(local_file):
        path = Path(local_file)
        if not path.exists():
            logging.getLogger().error('The path %(local_file)s was not found', dict(local_file=local_file))
            raise LocalFileNotFound(local_file)
        if not path.is_file():
            logging.getLogger().error('The path %(local_file)s is not a file', dict(local_file=local_file))
            raise LocalFileNotFound(local_file)

        return dict(
            name=path.name,
            size=str(path.stat().st_size),
            mimetype=mimetypes.guess_type(local_file)
        )

    @staticmethod
    def compute_zip_file_name(cloud_directory, files):
        if len(files) > 1:
            path = Path(cloud_directory)
        else:
            path = Path(files[0])
        return path.stem + '.zip'

    def get_dirpath(self):
        dirpath = config.filesystem['dl']
        try:
            self.validate_directory(dirpath)
        except LocalDirectoryNotFound as error:
            dirpath = self.expanduser(dirpath)
            logging.getLogger().error('Download failed. Check the following directory exists. %s', {'path': dirpath})
            raise error
        return dirpath

    @staticmethod
    def split_file_directory(path):
        # Exists and file -> directory=parent, filename=name
        # Exists and dir -> directory=current filename=None
        # Not Exists and parent Exists -> directory=parent filename=name
        # Not Exists and parent not Exists -> Error
        p = Path(path)
        if p.exists():
            if p.is_dir():
                filename = None
            else:
                filename = p.name
                p = p.parent
        elif p.parent.exists():
            filename = p.name
            p = p.parent
        else:
            raise LocalPathNotFound(path)
        return str(p.resolve()), filename
