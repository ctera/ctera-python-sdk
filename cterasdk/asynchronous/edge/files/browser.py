from ..base_command import BaseCommand
from ....cio.edge.commands import ListDirectory, RecursiveIterator, GetMetadata, Open, OpenMany, Upload, \
     UploadFile, CreateDirectory, Copy, Move, Delete, Download, DownloadMany
from . import io


class FileBrowser(BaseCommand):
    """ Edge Filer File Browser APIs """

    async def listdir(self, path):
        """
        List Directory

        :param str path: Path
        """
        for o in await ListDirectory(io.listdir, self._edge, path).a_execute():
            yield o

    async def walk(self, path=None):
        """
        Walk Directory Contents

        :param str, defaults to the root directory path: Path to walk
        """
        async for o in RecursiveIterator(io.listdir, self._edge, path).a_generate():
            yield o

    async def properties(self, path):
        """
        Get Properties
        
        :param str path: Path
        """
        async with GetMetadata(io.listdir, self._edge, path, True) as (_, metadata):
            return metadata

    async def exists(self, path):
        """
        Check if item exists

        :param str path: Path
        """
        async with GetMetadata(io.listdir, self._edge, path, True) as (exists, *_):
            return exists

    async def handle(self, path):
        """
        Get File Handle.

        :param str path: Path to a file
        """
        return await Open(io.handle, self._edge, path).a_execute()

    async def handle_many(self, directory, *objects):
        """
        Get a Zip Archive File Handle.

        :param str directory: Path to a folder
        :param args objects: List of files and folders
        """
        return await OpenMany(io.handle_many, self._edge, directory, *objects).a_execute()

    async def download(self, path, destination=None):
        """
        Download a file

        :param str path: The file path on the Edge Filer
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        return await Download(io.handle, self._edge, path, destination).a_execute()

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
        return await DownloadMany(io.handle_many, self._edge, target, objects, destination).a_execute()

    async def upload(self, name, destination, handle):
        """
        Upload from file handle.

        :param str name: File name.
        :param str destination: Path to remote directory.
        :param object handle: Handle.
        """
        return await Upload(io.upload, self._edge, io.listdir, name, destination, handle).a_execute()

    async def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path
        :param str destination: Remote path
        """
        return await UploadFile(io.upload, self._edge, io.listdir, path, destination).a_execute()

    async def mkdir(self, path):
        """
        Create a new directory

        :param str path: Directory path
        """
        return await CreateDirectory(io.mkdir, self._edge, path).a_execute()

    async def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return await CreateDirectory(io.mkdir, self._edge, path, True).a_execute()

    async def copy(self, path, destination=None, overwrite=False):
        """
        Copy a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        if destination is None:
            raise ValueError('Copy destination was not specified.')
        return await Copy(io.copy, self._edge, path, destination, overwrite).a_execute()

    async def move(self, path, destination=None, overwrite=False):
        """
        Move a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        if destination is None:
            raise ValueError('Move destination was not specified.')
        return await Move(io.move, self._edge, path, destination, overwrite).a_execute()

    async def delete(self, path):
        """
        Delete a file

        :param str path: File path
        """
        return await Delete(io.delete, self._edge, path).a_execute()
