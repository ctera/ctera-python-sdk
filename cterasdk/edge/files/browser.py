from ..base_command import BaseCommand
from ...cio.edge.commands import ListDirectory, RecursiveIterator, GetMetadata, Open, OpenMany, Upload, \
     CreateDirectory, Copy, Move, Delete, Download, DownloadMany, Rename, EnsureDirectory
from ...lib.storage import commonfs
from . import io


class FileBrowser(BaseCommand):
    """Edge Filer File Browser API."""

    def listdir(self, path=None):
        """
        List directory contents.

        :param str path: Path. Defaults to the root directory.
        :returns: Directory contents.
        :rtype: list[cterasdk.cio.edge.types.EdgeResource]
        :raises cterasdk.exceptions.io.core.GetMetadataError: If the directory was not found.
        :raises cterasdk.exceptions.io.core.NotADirectoryException: If the target path is not a directory.
        :raises cterasdk.exceptions.io.edge.ListDirectoryError: Raised on error to fetch directory contents.
        """
        with EnsureDirectory(io.listdir, self._edge, path):
            return ListDirectory(io.listdir, self._edge, path).execute()

    def walk(self, path=None):
        """
        Walk directory contents.

        :param str, optional path: Path to walk. Defaults to the root directory.
        :returns: A generator of file-system objects.
        :rtype: Iterator[cterasdk.cio.edge.types.EdgeResource]
        :raises cterasdk.exceptions.io.core.GetMetadataError: If the directory was not found.
        :raises cterasdk.exceptions.io.core.NotADirectoryException: If the target path is not a directory.
        """
        with EnsureDirectory(io.listdir, self._edge, path):
            return RecursiveIterator(io.listdir, self._edge, path).generate()

    def properties(self, path):
        """
        Get object properties.

        :param str path: Path.
        :returns: Object properties.
        :rtype: cterasdk.cio.edge.types.EdgeResource
        :raises cterasdk.exceptions.io.core.GetMetadataError: Raised on error to obtain object metadata.
        """
        with GetMetadata(io.listdir, self._edge, path, False) as (_, metadata):
            return metadata

    def exists(self, path):
        """
        Check whether an item exists.

        :param str path: Path.
        :returns: ``True`` if the item exists, ``False`` otherwise.
        :rtype: bool
        """
        with GetMetadata(io.listdir, self._edge, path, True) as (exists, *_):
            return exists

    def handle(self, path):
        """
        Get a file handle.

        :param str path: Path to a file.
        :returns: File handle.
        :rtype: object
        :raises cterasdk.exceptions.io.edge.OpenError: Raised on error to obtain a file handle.
        """
        return Open(io.handle, self._edge, path).execute()

    def handle_many(self, directory, *objects):
        """
        Get a ZIP archive file handle.

        :param str directory: Path to a folder.
        :param args objects: Files and folders to include.
        :returns: File handle.
        :rtype: object
        """
        return OpenMany(io.handle_many, self._edge, directory, *objects).execute()

    def download(self, path, destination=None):
        """
        Download a file.

        :param str path: The file path on the Edge Filer.
        :param str, optional destination:
            File destination. If a directory is provided, the original filename is preserved.
            Defaults to the default download directory.
        :returns: Path to the local file.
        :rtype: str
        :raises cterasdk.exceptions.io.edge.OpenError: Raised on error to obtain a file handle.
        """
        return Download(io.handle, self._edge, path, destination).execute()

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
            the original filename is preserved. Defaults to the default download directory.
        :returns: Path to the local file.
        :rtype: str
        """
        return DownloadMany(io.handle_many, self._edge, target, objects, destination).execute()

    def upload(self, destination, handle, name=None):
        """
        Upload from a file handle.

        :param str destination: Remote path.
        :param object handle: File-like handle.
        :param str, optional name: Filename to use if it cannot be derived from ``destination``
        :returns: Remote file path.
        :rtype: str
        :raises cterasdk.exceptions.io.edge.UploadError: Raised on upload failure.
        """
        return Upload(io.upload, self._edge, io.listdir, destination, handle, name).execute()

    def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path.
        :param str destination: Remote path.
        :returns: Remote file path.
        :rtype: str
        :raises cterasdk.exceptions.io.edge.UploadError: Raised on upload failure.
        """
        _, name = commonfs.split_file_directory(path)
        with open(path, 'rb') as handle:
            return self.upload(destination, handle, name)

    def mkdir(self, path):
        """
        Create a new directory.

        :param str path: Directory path.
        :returns: Remote directory path.
        :rtype: str
        :raises cterasdk.exceptions.io.edge.CreateDirectoryError: Raised on error to create a directory.
        """
        return CreateDirectory(io.mkdir, self._edge, path).execute()

    def makedirs(self, path):
        """
        Create a directory recursively.

        :param str path: Directory path.
        :returns: Remote directory path.
        :rtype: str
        :raises cterasdk.exceptions.io.edge.CreateDirectoryError: Raised on error to create a directory.
        """
        return CreateDirectory(io.mkdir, self._edge, path, True).execute()

    def copy(self, path, destination=None, overwrite=False):
        """
        Copy a file or directory.

        :param str path: Source file or directory path.
        :param str destination: Destination directory path.
        :param bool, optional overwrite: Overwrite on conflict. Defaults to ``False``.
        :raises cterasdk.exceptions.io.edge.CopyError: Raised on error to copy a file or directory.
        """
        return Copy(io.copy, self._edge, io.listdir, path, destination, overwrite).execute()

    def move(self, path, destination=None, overwrite=False):
        """
        Move a file or directory.

        :param str path: Source file or directory path.
        :param str destination: Destination directory path.
        :param bool, optional overwrite: Overwrite on conflict. Defaults to ``False``.
        :raises cterasdk.exceptions.io.edge.MoveError: Raised on error to move a file or directory.
        """
        return Move(io.move, self._edge, io.listdir, path, destination, overwrite).execute()

    def rename(self, path, new_name, overwrite=False):
        """
        Rename a file or directory.

        :param str path: Path of the file or directory to rename.
        :param str new_name: New name for the file or directory.
        :param bool, optional overwrite: Overwrite on conflict. Defaults to ``False``.
        :returns: Remote object path.
        :rtype: str
        :raises cterasdk.exceptions.io.edge.RenameError: Raised on error to rename a file or directory.
        """
        return Rename(io.move, self._edge, io.listdir, path, new_name, overwrite).execute()

    def delete(self, path):
        """
        Delete a file or directory.

        :param str path: File or directory path.
        :returns: Deleted object path.
        :rtype: str
        :raises cterasdk.exceptions.io.edge.DeleteError: Raised on error to delete a file or directory.
        """
        return Delete(io.delete, self._edge, path).execute()
