from .. import query
from ....cio.core import CorePath, Open, OpenMany, Upload, UploadFile, Download, \
    DownloadMany, UnShare, CreateDirectory, GetMetadata, ListVersions, RecursiveIterator, \
    Delete, Recover, Rename, GetShareMetadata, Link, Copy, Move, ResourceIterator, GetPermalink
from ..base_command import BaseCommand
from . import io


class FileBrowser(BaseCommand):

    def __init__(self, core):
        super().__init__(core)
        self._scope = f'/{self._core.context}/webdav'

    async def handle(self, path):
        """
        Get File Handle.

        :param str path: Path to a file
        """
        return await Open(io.handle, self._core, self.normalize(path)).a_execute()

    async def handle_many(self, directory, *objects):
        """
        Get a Zip Archive File Handle.

        :param str directory: Path to a folder
        :param args objects: List of files and folders
        """
        return await OpenMany(io.handle_many, self._core, self.normalize(directory), *objects).a_execute()

    async def download(self, path, destination=None):
        """
        Download a file

        :param str path: Path
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        return await Download(io.handle, self._core, self.normalize(path), destination).a_execute()

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
        return await DownloadMany(io.handle_many, self._core, self.normalize(target), objects, destination).a_execute()

    async def listdir(self, path=None, depth=None, include_deleted=False):
        """
        List Directory

        :param str,optional path: Path, defaults to the Cloud Drive root
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        async for o in ResourceIterator(query.iterator, self._core, self.normalize(path), depth, include_deleted, None, None).a_execute():
            yield o

    async def exists(self, path):
        """
        Check if item exists

        :param str path: Path
        """
        async with GetMetadata(io.listdir, self._core, self.normalize(path), True) as (exists, *_):
            return exists

    async def versions(self, path):
        """
        List snapshots of a file or directory

        :param str path: Path
        """
        return await ListVersions(io.versions, self._core, self.normalize(path)).a_execute()

    async def walk(self, path=None, include_deleted=False):
        """
        Walk Directory Contents

        :param str,optional path: Path to walk, defaults to the root directory
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        async for o in RecursiveIterator(query.iterator, self._core, self.normalize(path), include_deleted).a_generate():
            yield o

    async def public_link(self, path, access='RO', expire_in=30):
        """
        Create a public link to a file or a folder

        :param str path: The path of the file to create a link to
        :param str,optional access: Access policy of the link, defaults to 'RO'
        :param int,optional expire_in: Number of days until the link expires, defaults to 30
        """
        return await Link(io.public_link, self._core, self.normalize(path), access, expire_in).a_execute()

    async def copy(self, *paths, destination=None, resolver=None, cursor=None, wait=False):
        """
        Copy one or more files or folders

        :param list[str] paths: List of paths
        :param str destination: Destination
        :param cterasdk.core.types.ConflictResolver resolver: Conflict resolver, defaults to ``None``
        :param cterasdk.common.object.Object cursor: Resume copy from cursor
        :param bool,optional wait: ``True`` Wait for task to complete, or ``False`` to return an awaitable task object.
        :returns: Task status object, or an awaitable task object
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        """
        try:
            return await Copy(io.copy, self._core, wait, *[self.normalize(path) for path in paths],
                              destination=self.normalize(destination), resolver=resolver, cursor=cursor).a_execute()
        except ValueError:
            raise ValueError('Copy destination was not specified.')

    async def permalink(self, path):
        """
        Get Permalink for Path.

        :param str path: Path.
        """
        return await GetPermalink(io.listdir, self._core, self.normalize(path)).a_execute()

    def normalize(self, entries):
        return CorePath.instance(self._scope, entries)


class CloudDrive(FileBrowser):

    async def upload(self, name, destination, handle, size=None):
        """
        Upload from file handle.

        :param str name: File name.
        :param str destination: Path to remote directory.
        :param object handle: Handle.
        :param str,optional size: File size, defaults to content length
        """
        return await Upload(io.upload, self._core, io.listdir, name, self.normalize(destination), size, handle).a_execute()

    async def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path
        :param str destination: Remote path
        """
        return await UploadFile(io.upload, self._core, io.listdir, path, self.normalize(destination)).a_execute()

    async def mkdir(self, path):
        """
        Create a new directory

        :param str path: Directory path
        """
        return await CreateDirectory(io.mkdir, self._core, self.normalize(path)).a_execute()

    async def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return await CreateDirectory(io.mkdir, self._core, self.normalize(path), True).a_execute()

    async def rename(self, path, name, *, wait=False):
        """
        Rename a file

        :param str path: Path of the file or directory to rename
        :param str name: The name to rename to
        :param bool,optional wait: ``True`` Wait for task to complete, or ``False`` to return an awaitable task object.
        :returns: Task status object, or an awaitable task object
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        """
        return await Rename(io.move, self._core, self.normalize(path), name, wait).a_execute()

    async def delete(self, *paths, wait=False):
        """
        Delete one or more files or folders

        :param str path: Path
        :param bool,optional wait: ``True`` Wait for task to complete, or ``False`` to return an awaitable task object.
        :returns: Task status object, or an awaitable task object
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        """
        return await Delete(io.delete, self._core, wait, *[self.normalize(path) for path in paths]).a_execute()

    async def undelete(self, *paths, wait=False):
        """
        Recover one or more files or folders

        :param str path: Path
        :param bool,optional wait: ``True`` Wait for task to complete, or ``False`` to return an awaitable task object.
        :returns: Task status object, or an awaitable task object
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        """
        return await Recover(io.undelete, self._core, wait, *[self.normalize(path) for path in paths]).a_execute()

    async def move(self, *paths, destination=None, resolver=None, cursor=None, wait=False):
        """
        Move one or more files or folders

        :param list[str] paths: List of paths
        :param str destination: Destination
        :param cterasdk.core.types.ConflictResolver resolver: Conflict resolver, defaults to ``None``
        :param cterasdk.common.object.Object cursor: Resume copy from cursor
        :param bool,optional wait: ``True`` Wait for task to complete, or ``False`` to return an awaitable task object.
        :returns: Task status object, or an awaitable task object
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        """
        try:
            return await Move(io.move, self._core, wait, *[self.normalize(path) for path in paths],
                              destination=self.normalize(destination), resolver=resolver, cursor=cursor).a_execute()
        except ValueError:
            raise ValueError('Move destination was not specified.')

    async def get_share_info(self, path):
        """
        Get share settings and recipients

        :param str path: Path
        """
        return await GetShareMetadata(io.list_shares, self._core, self.normalize(path)).a_execute()

    async def share(self, path, recipients, as_project=True, allow_reshare=True, allow_sync=True):
        """
        Share a file or a folder

        :param str path: The path of the file or folder to share
        :param list[cterasdk.core.types.Collaborator] recipients: A list of share recipients
        :param bool,optional as_project: Share as a team project, defaults to True when the item is a cloud folder else False
        :param bool,optional allow_reshare: Allow recipients to re-share this item, defaults to True
        :param bool,optional allow_sync: Allow recipients to sync this item, defaults to True when the item is a cloud folder else False
        :return: A list of all recipients added to the collaboration share
        :rtype: list[cterasdk.core.types.Collaborator]
        """
        return await io.share(self._core, self.normalize(path), recipients, as_project, allow_reshare, allow_sync)

    async def add_share_recipients(self, path, recipients):
        """
        Add share recipients

        :param str path: The path of the file or folder
        :param list[cterasdk.core.types.Collaborator] recipients: A list of share recipients
        :return: A list of all recipients added
        :rtype: list[cterasdk.core.types.Collaborator]
        """
        return await io.add_share_recipients(self._core, self.normalize(path), recipients)

    async def remove_share_recipients(self, path, accounts):
        """
        Remove share recipients

        :param str path: The path of the file or folder
        :param list[cterasdk.core.types.PortalAccount] accounts: A list of portal user or group accounts
        :return: A list of all share recipients removed
        :rtype: list[cterasdk.core.types.PortalAccount]
        """
        return await io.remove_share_recipients(self._core, self.normalize(path), accounts)

    async def unshare(self, path):
        """
        Unshare a file or a folder
        """
        return await UnShare(io.update_share, self._core, self.normalize(path)).a_execute()
