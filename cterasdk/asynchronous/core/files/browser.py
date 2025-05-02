from ....cio.core import CorePath
from ....lib import FileSystem
from ..base_command import BaseCommand
from . import io


class FileBrowser(BaseCommand):

    def __init__(self, core):
        super().__init__(core)
        self._scope = f'/{self._core.context}/webdav'
        self._filesystem = FileSystem.instance()

    async def handle(self, path):
        """
        Get File Handle.

        :param str path: Path to a file
        """
        handle_function = await io.handle(self.normalize(path))
        return await handle_function(self._core)

    async def handle_many(self, directory, *objects):
        """
        Get a Zip Archive File Handle.

        :param str directory: Path to a folder
        :param args objects: List of files and folders
        """
        handle_many_function = await io.handle_many(self.normalize(directory), *objects)
        return await handle_many_function(self._core)

    async def listdir(self, path, depth=None, include_deleted=False):
        """
        List Directory

        :param str path: Path
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        return await io.listdir(self._core, self.normalize(path), depth=depth, include_deleted=include_deleted)

    async def versions(self, path):
        """
        List snapshots of a file or directory

        :param str path: Path
        """
        return await io.versions(self._core, self.normalize(path))

    async def walk(self, path, include_deleted=False):
        """
        Walk Directory Contents

        :param str path: Path to walk
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

    async def copy(self, *paths, destination=None):
        """
        Copy one or more files or folders

        :param list[str] paths: List of paths
        :param str destination: Destination
        """
        if destination is None:
            raise ValueError('Copy destination was not specified.')
        return await io.copy(self._core, *[self.normalize(path) for path in paths], destination=self.normalize(destination))

    async def permalink(self, path):
        """
        Get Permalink for Path.

        :param str path: Path.
        """
        p = self.normalize(path)
        contents = [e async for e in await io.listdir(self._core,
                                                      p.parent, 1, False, p.name, 1)]  # pylint: disable=unnecessary-comprehension
        if contents and contents[0].name == p.name:
            return contents[0].permalink
        raise FileNotFoundError('File not found.', path)

    def normalize(self, entries):
        return CorePath.instance(self._scope, entries)


class CloudDrive(FileBrowser):

    async def upload(self, name, size, destination, handle):
        """
        Upload from file handle.

        :param str name: File name.
        :param str size: File size.
        :param str destination: Path to remote directory.
        :param object handle: Handle.
        """
        upload_function = await io.upload(name, size, self.normalize(destination), handle)
        return await upload_function(self._core)

    async def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path
        :param str destination: Remote path
        """
        with open(path, 'rb') as handle:
            metadata = self._filesystem.properties(path)
            response = await self.upload(metadata['name'], metadata['size'], destination, handle)
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

    async def rename(self, path, name):
        """
        Rename a file

        :param str path: Path of the file or directory to rename
        :param str name: The name to rename to
        """
        return await io.rename(self._core, self.normalize(path), name)

    async def delete(self, *paths):
        """
        Delete one or more files or folders

        :param str path: Path
        """
        return await io.remove(self._core, *[self.normalize(path) for path in paths])

    async def undelete(self, *paths):
        """
        Recover one or more files or folders

        :param str path: Path
        """
        return await io.recover(self._core, *[self.normalize(path) for path in paths])

    async def move(self, *paths, destination=None):
        """
        Move one or more files or folders

        :param list[str] paths: List of paths
        :param str destination: Destination
        """
        if destination is None:
            raise ValueError('Move destination was not specified.')
        return await io.move(self._core, *[self.normalize(path) for path in paths], destination=self.normalize(destination))
