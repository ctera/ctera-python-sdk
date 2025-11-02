from ..base_command import BaseCommand
from ...cio.edge import EdgePath, ListDirectory, RecursiveIterator, GetMetadata, Open, OpenMany, Upload, \
     UploadFile, CreateDirectory, Copy, Move, Delete, Download, DownloadMany, Rename
from . import io


class FileBrowser(BaseCommand):
    """ Edge Filer File Browser APIs """

    def listdir(self, path):
        """
        List Directory

        :param str path: Path
        """
        return ListDirectory(io.listdir, self._edge, self.normalize(path)).execute()

    def walk(self, path=None):
        """
        Walk Directory Contents

        :param str,optional path: Path to walk, defaults to the root directory
        """
        return RecursiveIterator(io.listdir, self._edge, self.normalize(path)).generate()

    def exists(self, path):
        """
        Check if item exists

        :param str path: Path
        """
        with GetMetadata(io.listdir, self._edge, self.normalize(path), True) as (exists, *_):
            return exists

    def handle(self, path):
        """
        Get File Handle.

        :param str path: Path to a file
        """
        return Open(io.handle, self._edge, self.normalize(path)).execute()

    def handle_many(self, directory, *objects):
        """
        Get a Zip Archive File Handle.

        :param str directory: Path to a folder
        :param args objects: List of files and folders
        """
        return OpenMany(io.handle_many, self._edge, directory, *objects).execute()

    def download(self, path, destination=None):
        """
        Download a file

        :param str path: The file path on the Edge Filer
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        return Download(io.handle, self._edge, self.normalize(path), destination).execute()

    def download_many(self, target, objects, destination=None):
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
        return DownloadMany(io.handle_many, self._edge, self.normalize(target), objects, destination).execute()

    def upload(self, name, destination, handle):
        """
        Upload from file handle.

        :param str name: File name.
        :param str destination: Path to remote directory.
        :param object handle: Handle.
        """
        return Upload(io.upload, self._edge, io.listdir, name, self.normalize(destination), handle).execute()

    def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path
        :param str destination: Remote path
        """
        return UploadFile(io.upload, self._edge, io.listdir, path, self.normalize(destination)).execute()

    def mkdir(self, path):
        """
        Create a new directory

        :param str path: Directory path
        """
        return CreateDirectory(io.mkdir, self._edge, self.normalize(path)).execute()

    def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return CreateDirectory(io.mkdir, self._edge, self.normalize(path), True).execute()

    def copy(self, path, destination=None, overwrite=False):
        """
        Copy a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        return Copy(io.copy, self._edge, self.normalize(path), self.normalize(destination), overwrite).execute()

    def move(self, path, destination=None, overwrite=False):
        """
        Move a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        return Move(io.move, self._edge, self.normalize(path), self.normalize(destination), overwrite).execute()

    def rename(self, path, name):
        """
        Rename a file

        :param str path: Path of the file or directory to rename
        :param str name: The name to rename to
        """
        return Rename(io.move, self._edge, self.normalize(path), name).execute()

    def delete(self, path):
        """
        Delete a file

        :param str path: File path
        """
        return Delete(io.delete, self._edge, self.normalize(path)).execute()

    @staticmethod
    def normalize(path):
        return EdgePath.instance('/', path)
