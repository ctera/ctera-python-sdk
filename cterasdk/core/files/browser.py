from .. import query
from ...cio.core.commands import Open, OpenMany, Upload, Download, EnsureDirectory, \
    DownloadMany, UnShare, CreateDirectory, GetMetadata, GetProperties, ListVersions, RecursiveIterator, \
    Delete, Recover, Rename, GetShareMetadata, Link, Copy, Move, ResourceIterator, GetPermalink
from ...lib.storage import commonfs
from ..base_command import BaseCommand
from . import io


class FileBrowser(BaseCommand):
    """CTERA Portal File Browser API."""

    def handle(self, path):
        """
        Get a file handle.

        :param str path: Path to a file.
        :returns: File handle.
        :rtype: object
        :raises cterasdk.exceptions.io.core.OpenError: Raised on error to obtain a file handle.
        """
        return Open(io.handle, self._core, path).execute()

    def handle_many(self, directory, *objects):
        """
        Get a ZIP archive file handle.

        :param str directory: Path to a folder.
        :param args objects: Files and folders to include.
        :returns: File handle.
        :rtype: object
        :raises cterasdk.exceptions.io.core.GetMetadataError: If the directory was not found.
        :raises cterasdk.exceptions.io.core.NotADirectoryException: If the target path is not a directory.
        """
        with EnsureDirectory(io.listdir, self._core, directory) as (_, resource):
            return OpenMany(io.handle_many, self._core, resource, directory, *objects).execute()

    def download(self, path, destination=None):
        """
        Download a file.

        :param str path: Path.
        :param str, optional destination: File destination. If a directory is provided, the original filename is preserved.
         Defaults to the default download directory.
        :returns: Path to the local file.
        :rtype: str
        :raises cterasdk.exceptions.io.core.OpenError: Raised on error to obtain a file handle.
        """
        return Download(io.handle, self._core, path, destination).execute()

    def download_many(self, directory, objects, destination=None):
        """
        Download selected files and/or directories as a ZIP archive.

        .. warning::
            Only existing files and directories will be included in the resulting ZIP file.

        :param str directory: Path to a folder.
        :param list[str] objects: List of files and / or directory names to download.
        :param str destination: Optional path to destination file or directory. Defaults to the default download directory.
        :returns: Path to the local file.
        :rtype: str
        :raises cterasdk.exceptions.io.core.GetMetadataError: If the directory was not found.
        :raises cterasdk.exceptions.io.core.NotADirectoryException: If the target path is not a directory.
        """
        with EnsureDirectory(io.listdir, self._core, directory) as (_, resource):
            return DownloadMany(io.handle_many, self._core, resource, directory, objects, destination).execute()

    def listdir(self, path=None, include_deleted=False):
        """
        List directory contents.

        :param str, optional path: Path. Defaults to the Cloud Drive root.
        :param bool, optional include_deleted: Include deleted files. Defaults to False.
        :returns: Directory contents.
        :rtype: list[cterasdk.cio.core.types.PortalResource]
        :raises cterasdk.exceptions.io.core.GetMetadataError: If the directory was not found.
        :raises cterasdk.exceptions.io.core.NotADirectoryException: If the target path is not a directory.
        :raises cterasdk.exceptions.io.core.ListDirectoryError: Raised on error fetching directory contents.
        """
        with EnsureDirectory(io.listdir, self._core, path):
            return ResourceIterator(query.iterator, self._core, path, None, include_deleted, None, None).execute()

    def properties(self, path):
        """
        Get object properties.

        :param str path: Path.
        :returns: Object properties.
        :rtype: cterasdk.cio.core.types.PortalResource
        :raises cterasdk.exceptions.io.core.GetMetadataError: Raised on error retrieving object metadata.
        """
        _, metadata = GetProperties(io.listdir, self._core, path, False).execute()
        return metadata

    def exists(self, path):
        """
        Check whether an item exists.

        :param str path: Path.
        :returns: True if the item exists, False otherwise.
        :rtype: bool
        """
        with GetMetadata(io.listdir, self._core, path, True) as (exists, *_):
            return exists

    def versions(self, path):
        """
        List snapshots of a file or directory.

        :param str path: Path.
        :returns: List of versions.
        :rtype: list[cterasdk.cio.core.types.PreviousVersion]
        :raises cterasdk.exceptions.io.core.GetVersionsError: Raised on error retrieving versions.
        """
        return ListVersions(io.versions, self._core, path).execute()

    def walk(self, path=None, include_deleted=False):
        """
        Walk directory contents.

        :param str, optional path: Path to walk. Defaults to the root directory.
        :param bool, optional include_deleted: Include deleted files. Defaults to False.
        :returns: A generator of file-system objects.
        :rtype: Iterator[cterasdk.cio.core.types.PortalResource]
        :raises cterasdk.exceptions.io.core.GetMetadataError: If the directory was not found.
        :raises cterasdk.exceptions.io.core.NotADirectoryException: If the target path is not a directory.
        """
        with EnsureDirectory(io.listdir, self._core, path):
            return RecursiveIterator(query.iterator, self._core, path, include_deleted).generate()

    def public_link(self, path, access='RO', expire_in=30):
        """
        Create a public link to a file or folder.

        :param str path: Path of the file or folder.
        :param str, optional access: Access policy of the link. Defaults to 'RO'.
        :param int, optional expire_in: Days until link expires. Defaults to 30.
        :returns: Public link.
        :rtype: str
        :raises cterasdk.exceptions.io.core.CreateLinkError: Raised on failure to generate public link.
        """
        return Link(io.public_link, self._core, path, access, expire_in).execute()

    def copy(self, *paths, destination=None, resolver=None, cursor=None, wait=True):
        """
        Copy one or more files or folders.

        :param list[str] paths: Paths to copy.
        :param str destination: Destination path.
        :param cterasdk.core.types.ConflictResolver, optional resolver: Conflict resolver. Defaults to None.
        :param cterasdk.common.object.Object cursor: Resume copy from cursor.
        :param bool, optional wait: Wait for task completion. Defaults to True.
        :returns: Task status object, or awaitable task.
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        :raises cterasdk.exceptions.io.core.CopyError: Raised on failure to copy resources.
        """
        try:
            return Copy(io.copy, self._core, wait, *paths, destination=destination, resolver=resolver, cursor=cursor).execute()
        except ValueError:
            raise ValueError('Copy destination was not specified.')

    def permalink(self, path):
        """
        Get permalink for a path.

        :param str path: Path.
        :returns: Permalink.
        :rtype: str
        :raises cterasdk.exceptions.io.core.GetMetadataError: Raised on error retrieving object metadata.
        """
        return GetPermalink(io.listdir, self._core, path).execute()


class CloudDrive(FileBrowser):
    """CloudDrive extends FileBrowser with upload and share functionality."""

    def upload(self, destination, handle, name=None, size=None):
        """
        Upload from file handle.

        :param str destination: Remote path.
        :param object handle: File-like handle.
        :param str, optional size: File size. Defaults to content length.
        :param str, optional name: Filename to use if it cannot be derived from ``destination``
        :returns: Remote file path.
        :rtype: str
        :raises cterasdk.exceptions.io.core.UploadError: Raised on upload failure.
        """
        return Upload(io.upload, self._core, io.listdir, destination, handle, name, size).execute()

    def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path.
        :param str destination: Remote path.
        :returns: Remote file path.
        :rtype: str
        :raises cterasdk.exceptions.io.core.UploadError: Raised on upload failure.
        """
        _, name = commonfs.split_file_directory(path)
        with open(path, 'rb') as handle:
            return self.upload(destination, handle, name, commonfs.properties(path)['size'])

    def mkdir(self, path):
        """
        Create a directory.

        :param str path: Directory path.
        :returns: Remote directory path.
        :rtype: str
        :raises cterasdk.exceptions.io.core.CreateDirectoryError: Raised on error creating directory.
        """
        return CreateDirectory(io.mkdir, self._core, path).execute()

    def makedirs(self, path):
        """
        Recursively create a directory.

        :param str path: Directory path.
        :returns: Remote directory path.
        :rtype: str
        :raises cterasdk.exceptions.io.core.CreateDirectoryError: Raised on error creating directory.
        """
        return CreateDirectory(io.mkdir, self._core, path, True).execute()

    def rename(self, path, name, *, resolver=None, wait=True):
        """
        Rename a file or folder.

        :param str path: Path of the file or directory.
        :param str name: New name.
        :param cterasdk.core.types.ConflictResolver, optional resolver: Conflict resolver. Defaults None.
        :param bool, optional wait: Wait for task completion. Defaults to True.
        :returns: Task status object, or awaitable task.
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        :raises cterasdk.exceptions.io.core.RenameError: Raised on error renaming object.
        """
        return Rename(io.move, self._core, wait, path, name, resolver).execute()

    def delete(self, *paths, wait=True):
        """
        Delete one or more files or folders.

        :param list[str] paths: Paths to delete.
        :param bool, optional wait: Wait for task completion. Defaults to True.
        :returns: Task status object, or awaitable task.
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        :raises cterasdk.exceptions.io.core.DeleteError: Raised on error deleting resources.
        """
        return Delete(io.delete, self._core, wait, *paths).execute()

    def undelete(self, *paths, wait=True):
        """
        Recover one or more files or folders.

        :param list[str] paths: Paths to recover.
        :param bool, optional wait: Wait for task completion. Defaults to True.
        :returns: Task status object, or awaitable task.
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        :raises cterasdk.exceptions.io.core.RecoverError: Raised on error recovering resources.
        """
        return Recover(io.undelete, self._core, wait, *paths).execute()

    def move(self, *paths, destination=None, resolver=None, cursor=None, wait=True):
        """
        Move one or more files or folders.

        :param list[str] paths: Paths to move.
        :param str destination: Destination path.
        :param cterasdk.core.types.ConflictResolver, optional resolver: Conflict resolver. Defaults to None.
        :param cterasdk.common.object.Object cursor: Resume move from cursor.
        :param bool, optional wait: Wait for task completion. Defaults to True.
        :returns: Task status object, or awaitable task.
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        :raises cterasdk.exceptions.io.core.MoveError: Raised on error moving resources.
        """
        try:
            return Move(io.move, self._core, wait, *paths, destination=destination, resolver=resolver, cursor=cursor).execute()
        except ValueError:
            raise ValueError('Move destination was not specified.')

    def get_share_info(self, path):
        """
        Get share settings and recipients.

        :param str path: Path.
        :returns: Share metadata.
        :rtype: object
        :raises cterasdk.exceptions.io.core.GetShareMetadataError: Raised on error obtaining share metadata.
        """
        return GetShareMetadata(io.list_shares, self._core, path).execute()

    def share(self, path, recipients, as_project=True, allow_reshare=True, allow_sync=True):
        """
        Share a file or folder.

        :param str path: Path of the file or folder to share.
        :param list[cterasdk.core.types.Collaborator] recipients: Share recipients.
        :param bool, optional as_project: Share as a team project. Defaults True if cloud folder.
        :param bool, optional allow_reshare: Allow re-share. Defaults True.
        :param bool, optional allow_sync: Allow sync. Defaults True if cloud folder.
        :returns: Current list of share members.
        :rtype: list[cterasdk.core.types.Collaborator]
        """
        return io.share(self._core, path, recipients, as_project, allow_reshare, allow_sync)

    def add_share_recipients(self, path, recipients):
        """
        Add share recipients.

        :param str path: Path of file/folder.
        :param list[cterasdk.core.types.Collaborator] recipients: Recipients to add.
        :returns: Current list of share members.
        :rtype: list[cterasdk.core.types.Collaborator]
        """
        return io.add_share_recipients(self._core, path, recipients)

    def remove_share_recipients(self, path, accounts):
        """
        Remove share recipients.

        :param str path: Path of file/folder.
        :param list[cterasdk.core.types.PortalAccount] accounts: Accounts to remove.
        :returns: Current list of share members.
        :rtype: list[cterasdk.core.types.Collaborator]
        """
        return io.remove_share_recipients(self._core, path, accounts)

    def unshare(self, path):
        """
        Unshare a file or folder.

        :param str path: Path of file/folder.
        """
        return UnShare(io.update_share, self._core, path).execute()


class Backups(FileBrowser):
    """Backup management API."""

    def device_config(self, device, destination=None):
        """
        Download a device configuration file.

        :param str device: Device name.
        :param str, optional destination: File destination. If a directory is provided, original filename is preserved.
         Defaults to default downloads directory.
        :returns: Path to local file.
        :rtype: str
        :raises cterasdk.exceptions.io.core.OpenError: Raised on error obtaining file handle.
        """
        destination = destination if destination is not None else f'{commonfs.downloads()}/{device}.xml'
        return Download(io.handle, self._core, f'backups/{device}/Device Configuration/db.xml', destination).execute()
