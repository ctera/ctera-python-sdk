import os
import errno
import mimetypes
import logging
from pathlib import Path

import aiofiles
import cterasdk.settings


class FileSystem:  # pylint: disable=unused-private-member

    __instance = None

    def __init__(self):
        if FileSystem.__instance is not None:
            raise Exception("FileSystem is a Singleton Class.")
        FileSystem.__instance = self

    @staticmethod
    def instance():
        if FileSystem.__instance is None:
            FileSystem()
        return FileSystem.__instance

    @staticmethod
    def expanduser(p):
        """
        Return a new path with expanded ~ and ~user constructs

        :param str p: Path
        :returns: Absolute Path.
        :rtype: str
        """
        return Path(p).expanduser()

    @staticmethod
    def exists(p):
        """
        Check if a file or a directory exists

        :param str p: Path
        :returns: ``True`` if exists, ``False`` otherwise.
        :rtype: bool
        """
        return Path(p).exists()

    def rename(self, parent, source, destination):  # pylint: disable=no-self-use
        """
        Rename a file or a directory.

        :param str parent: Parent directory
        :param str source: Source file or directory name
        :param str destination: Destination file or directory name
        :returns: Parent directory, and file or directory name
        :rtype: tuple(str, str)
        """
        source = Path(parent).joinpath(source)
        if not source.exists():
            logging.getLogger('cterasdk.filesystem').error('Rename failed. File not found. %s', {'path': source.as_posix()})
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), source.as_posix())
        destination = Path(parent).joinpath(destination)
        source.rename(destination)
        return destination.parent.as_posix(), destination.name

    @staticmethod
    def join(*paths):
        return Path(*paths)

    def is_dir(self, p):
        """
        Check is a directory.

        :param str p: Path
        :returns: ``True`` if a directory, ``False`` otherwise.
        :rtype: bool
        """
        p = self.expanduser(p)
        return p.is_dir()

    def downloads_directory(self):
        """
        Get downloads directory.

        :returns: Directory Path
        :rtype: str
        """
        location = cterasdk.settings.downloads.location
        if not self.is_dir(location):
            logging.getLogger('cterasdk.filesystem').error('Could not find downloads directory. %s', {'path': location})
            raise FileNotFoundError(errno.ENOENT, 'No such directory', location)
        return location

    def split_file_directory(self, location):
        """
        Split file and directory.

        :param str path: Path

        Returns:
        1. (parent directory, file name), if a file exists
        2. (parent directory, file name), if a directory exists
        3. (parent directory, file name), if the parent directory exists
        4. Raises ``FileNotFoundError`` if neither the object nor the parent directory exist
        """
        p = self.expanduser(location)
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
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), location)
        return str(p.resolve()), filename

    def generate_file_location(self, location=None, default_filename=None):
        """
        Compute destination file path.

        :param str location: Path to a file or a folder
        :param str default_filename: Default file name, unless ``location`` already specifies a file path
        :returns: Tuple including the destination directory and file name
        :rtype: tuple(str, str)
        """
        parent = filename = None
        if location:
            parent, filename = self.split_file_directory(location)
        else:
            parent = self.downloads_directory()

        if not filename:
            filename = default_filename

        return (parent, filename)

    def properties(self, location):
        """
        Get file properties.

        :param str location: Path
        :returns: File name, size and type
        :rtype: dict
        """
        p = self.expanduser(location)

        if not p.exists():
            logging.getLogger('cterasdk.filesystem').error('File not found. %s', {'path': p.as_posix()})
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), p.as_posix())

        if not p.is_file():
            logging.getLogger('cterasdk.filesystem').error('No such file. %s', {'path': p.as_posix()})
            raise FileNotFoundError(errno.ENOENT, 'Not such file', p.as_posix())

        return dict(name=p.name, size=str(p.stat().st_size), mimetype=mimetypes.guess_type(location))

    @staticmethod
    def file_version(filename, version):
        """
        Append version number to file name.

        :param str filename: File name
        :param int version: File version
        :returns: File name appended with a version number
        :rtype: str
        """
        idx = filename.rfind('.')
        extension = ''
        if idx > 0:
            name = filename[:idx]
            extension = filename[idx:]
        else:
            name = filename
        return f'{name} ({str(version)}){extension}'

    @staticmethod
    def compute_zip_file_name(cloud_directory, files):
        """
        Compute zip file name.
        """
        if len(files) > 1:
            path = Path(cloud_directory)
        else:
            path = Path(files[0])
        return f'{path.stem}.zip'

    def _before_save(self, directory, filename):
        """
        Check directory exists, and compute temporary file name.
        """
        parent = self.expanduser(directory)
        if not parent.exists():
            raise FileNotFoundError(errno.ENOENT, 'No such directory', directory)

        temporary_file = parent.joinpath(f'{filename}.ctera')
        return (parent, temporary_file)

    def _after_write(self, parent, temporary_file, filename):
        """
        Move file to its final destination.
        """
        origin = filename
        version = 0
        while True:
            try:
                self.rename(parent, temporary_file.as_posix(), filename)
                break
            except (FileExistsError, IsADirectoryError):
                logging.getLogger('cterasdk.filesystem').debug('File exists. %s', {'path': parent.as_posix(), 'name': filename})
                version = version + 1
                filename = self.file_version(origin, version)

        filepath = parent.joinpath(filename)
        logging.getLogger('cterasdk.filesystem').info('Saved. %s', {'path': filepath.as_posix()})
        return filepath.as_posix()

    def save(self, directory, filename, handle):
        """
        Save file.

        :param str parent: Directory path.
        :param str filename: File name.
        :param object handle: File handle.
        :returns: File path
        :rtype: str
        """
        parent, temporary_file = self._before_save(directory, filename)  # Check directory exists, and compute temporary file name.
        self.write(temporary_file, handle)  # Write temporary file.
        return self._after_write(parent, temporary_file, filename)  # Rename to destination

    @staticmethod
    def write(p, handle):
        with open(p, 'w+b') as fd:
            if isinstance(handle, bytes):
                fd.write(handle)
            else:
                for chunk in handle.iter_content(chunk_size=8192):
                    fd.write(chunk)
        logging.getLogger('cterasdk.filesystem').debug('Write Complete. %s', {'path': p})

    @staticmethod
    async def async_write(p, handle):
        async with aiofiles.open(p, 'w+b') as fd:
            async for chunk in handle.async_iter_content(chunk_size=8192):
                await fd.write(chunk)
        logging.getLogger('cterasdk.filesystem').debug('Write Complete. %s', {'path': p})
