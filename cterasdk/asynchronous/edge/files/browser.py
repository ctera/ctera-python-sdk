from ..base_command import BaseCommand
from ....cio.edge import EdgePath
from ....lib.storage import asynfs, commonfs
from . import io


class FileBrowser(BaseCommand):
    """ Edge Filer File Browser APIs """

    async def listdir(self, path):
        """
        List Directory

        :param str path: Path
        """
        return await io.listdir(self._edge, self.normalize(path))

    async def walk(self, path=None):
        """
        Walk Directory Contents

        :param str, defaults to the root directory path: Path to walk
        """
        return io.walk(self._edge, path)

    async def exists(self, path):
        """
        Check if item exists

        :param str path: Path
        """
        return await io.exists(self._edge, self.normalize(path))

    async def handle(self, path):
        """
        Get File Handle.

        :param str path: Path to a file
        """
        handle_function = io.handle(self.normalize(path))
        return await handle_function(self._edge)

    async def handle_many(self, directory, *objects):
        """
        Get a Zip Archive File Handle.

        :param str directory: Path to a folder
        :param args objects: List of files and folders
        """
        handle_many_function = io.handle_many(self.normalize(directory), *objects)
        return await handle_many_function(self._edge)

    async def download(self, path, destination=None):
        """
        Download a file

        :param str path: The file path on the Edge Filer
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        directory, name = commonfs.determine_directory_and_filename(path, destination=destination)
        handle = await self.handle(path)
        return await asynfs.write(directory, name, handle)

    async def download_many(self, target, objects, destination=None):
        """
        Download selected files and/or directories as a ZIP archive.

        .. warning::
            The provided list of objects is not validated. Only existing files and directories
            will be included in the resulting ZIP file.

        :param str target:
            Path to the cloud folder containing the files and directories to download.
        :param list[str] objects:
            List of file and/or directory names to include in the download.
        :param str destination:
            Optional. Path to the destination file or directory. If a directory is provided,
            the original filename will be preserved. Defaults to the default download directory.
        """
        directory, name = commonfs.determine_directory_and_filename(target, objects, destination=destination, archive=True)
        handle = await self.handle_many(target, *objects)
        return await asynfs.write(directory, name, handle)

    async def upload(self, name, destination, handle):
        """
        Upload from file handle.

        :param str name: File name.
        :param str destination: Path to remote directory.
        :param object handle: Handle.
        """
        upload_function = io.upload(name, self.normalize(destination), handle)
        return await upload_function(self._edge)

    async def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path
        :param str destination: Remote path
        """
        metadata = commonfs.properties(path)
        with open(path, 'rb') as handle:
            response = await self.upload(metadata['name'], destination, handle)
        return response

    async def mkdir(self, path):
        """
        Create a new directory

        :param str path: Directory path
        """
        return await io.mkdir(self._edge, self.normalize(path))

    async def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return await io.makedirs(self._edge, self.normalize(path))

    async def copy(self, path, destination=None, overwrite=False):
        """
        Copy a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        if destination is None:
            raise ValueError('Copy destination was not specified.')
        return await io.copy(self._edge, self.normalize(path), self.normalize(destination), overwrite)

    async def move(self, path, destination=None, overwrite=False):
        """
        Move a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        if destination is None:
            raise ValueError('Move destination was not specified.')
        return await io.move(self._edge, self.normalize(path), self.normalize(destination), overwrite)

    async def delete(self, *paths):
        """
        Delete a file

        :param str path: File path
        """
        return await io.remove(self._edge, *[self.normalize(path) for path in paths])

    @staticmethod
    def normalize(path):
        return EdgePath('/', path)
