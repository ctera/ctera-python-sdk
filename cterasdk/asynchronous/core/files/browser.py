from ....cio.core import CorePath, a_await_or_future
from ....lib.storage import asynfs, commonfs
from ....exceptions.io import FileConflict
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
        handle_function = io.handle(self.normalize(path))
        return await handle_function(self._core)

    async def handle_many(self, directory, *objects):
        """
        Get a Zip Archive File Handle.

        :param str directory: Path to a folder
        :param args objects: List of files and folders
        """
        handle_many_function = io.handle_many(self.normalize(directory), *objects)
        return await handle_many_function(self._core)

    async def download(self, path, destination=None):
        """
        Download a file

        :param str path: Path
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

    async def listdir(self, path=None, depth=None, include_deleted=False):
        """
        List Directory

        :param str,optional path: Path, defaults to the Cloud Drive root
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        return await io.listdir(self._core, self.normalize(path), depth=depth, include_deleted=include_deleted)

    async def exists(self, path):
        """
        Check if item exists

        :param str path: Path
        """
        return await io.exists(self._core, self.normalize(path))

    async def versions(self, path):
        """
        List snapshots of a file or directory

        :param str path: Path
        """
        return await io.versions(self._core, self.normalize(path))

    async def walk(self, path=None, include_deleted=False):
        """
        Walk Directory Contents

        :param str,optional path: Path to walk, defaults to the root directory
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        return io.walk(self._core, self._scope, path, include_deleted=include_deleted)

    async def public_link(self, path, access='RO', expire_in=30):
        """
        Create a public link to a file or a folder

        :param str path: The path of the file to create a link to
        :param str,optional access: Access policy of the link, defaults to 'RO'
        :param int,optional expire_in: Number of days until the link expires, defaults to 30
        """
        return await io.public_link(self._core, self.normalize(path), access, expire_in)

    async def _try_with_resolver(self, func, *paths, destination=None, resolver=None, cursor=None, wait=False):
        async def wrapper(resume_from=None):
            ref = await func(self._core, *paths, destination=destination, resolver=resolver, cursor=resume_from)
            return await a_await_or_future(self._core, ref, wait)
        
        try:
            return await wrapper(cursor)
        except FileConflict as e:
            if resolver:
                return await wrapper(e.cursor)
            raise

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
            return await self._try_with_resolver(io.copy, *[self.normalize(path) for path in paths],
                                           destination=self.normalize(destination),
                                           resolver=resolver, cursor=cursor, wait=wait)
        except ValueError:
            raise ValueError('Copy destination was not specified.')

    async def permalink(self, path):
        """
        Get Permalink for Path.

        :param str path: Path.
        """
        p = self.normalize(path)
        async for e in await io.listdir(self._core, p.parent, 1, False, p.name, 1):
            if e.name == p.name:
                return e.permalink
        raise FileNotFoundError('File not found.', path)

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
        upload_function = io.upload(name, size, self.normalize(destination), handle)
        return await upload_function(self._core)

    async def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path
        :param str destination: Remote path
        """
        with open(path, 'rb') as handle:
            metadata = commonfs.properties(path)
            response = await self.upload(metadata['name'], destination, handle, metadata['size'])
        return response

    async def mkdir(self, path):
        """
        Create a new directory

        :param str path: Directory path
        """
        return await io.mkdir(self._core, self.normalize(path))

    async def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return await io.makedirs(self._core, self.normalize(path))

    async def rename(self, path, name, *, wait=False):
        """
        Rename a file

        :param str path: Path of the file or directory to rename
        :param str name: The name to rename to
        :param bool,optional wait: ``True`` Wait for task to complete, or ``False`` to return an awaitable task object.
        :returns: Task status object, or an awaitable task object
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        """
        ref = await io.rename(self._core, self.normalize(path), name)
        return await a_await_or_future(self._core, ref, wait)

    async def delete(self, *paths, wait=False):
        """
        Delete one or more files or folders

        :param str path: Path
        :param bool,optional wait: ``True`` Wait for task to complete, or ``False`` to return an awaitable task object.
        :returns: Task status object, or an awaitable task object
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        """
        ref = await io.remove(self._core, *[self.normalize(path) for path in paths])
        return await a_await_or_future(self._core, ref, wait)

    async def undelete(self, *paths, wait=False):
        """
        Recover one or more files or folders

        :param str path: Path
        :param bool,optional wait: ``True`` Wait for task to complete, or ``False`` to return an awaitable task object.
        :returns: Task status object, or an awaitable task object
        :rtype: cterasdk.common.object.Object or :class:`cterasdk.lib.tasks.AwaitablePortalTask`
        """
        ref = await io.recover(self._core, *[self.normalize(path) for path in paths])
        return await a_await_or_future(self._core, ref, wait)

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
            return await self._try_with_resolver(io.move, *[self.normalize(path) for path in paths],
                                           destination=self.normalize(destination),
                                           resolver=resolver, cursor=cursor, wait=wait)
        except ValueError:
            raise ValueError('Move destination was not specified.')
