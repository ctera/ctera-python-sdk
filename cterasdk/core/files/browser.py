import logging

import cterasdk.settings
from ...cio.core import CorePath
from ...exceptions import CTERAException
from ...lib import FileSystem
from ..base_command import BaseCommand
from . import io


class FileBrowser(BaseCommand):

    def __init__(self, core):
        super().__init__(core)
        self._scope = f'/{self._core.context}/webdav'
        self._filesystem = FileSystem.instance()

    def handle(self, path):
        """
        Get File Handle.

        :param str path: Path to a file
        """
        handle_function = io.handle(self.normalize(path))
        return handle_function(self._core)

    def handle_many(self, directory, *objects):
        """
        Get a Zip Archive File Handle.

        :param str directory: Path to a folder
        :param args objects: List of files and folders
        """
        handle_many_function = io.handle_many(self.normalize(directory), *objects)
        return handle_many_function(self._core)

    def download(self, path, destination=None):
        """
        Download a file

        :param str path: Path
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        directory, name = self.determine_directory_and_filename(path, destination=destination)
        handle = self.handle(path)
        return self._filesystem.save(directory, name, handle)

    def download_as_zip(self, target, objects, destination=None):
        """
        Download a list of files and/or directories from a cloud folder as a ZIP file

        .. warning:: The list of files is not validated. The ZIP file will include only the existing  files and directories

        :param str target: Path to the cloud directory
        :param list[str] objects: List of files and/or directories in the cloud folder to download
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        directory, name = self.determine_directory_and_filename(target, objects, destination=destination, archive=True)
        handle = self.handle_many(target, *objects)
        return self._filesystem.save(directory, name, handle)

    def listdir(self, path, depth=None, include_deleted=False):
        """
        List Directory

        :param str path: Path
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        return io.listdir(self._core, self.normalize(path), depth=depth, include_deleted=include_deleted)

    def versions(self, path):
        """
        List snapshots of a file or directory

        :param str path: Path
        """
        return io.versions(self._core, self.normalize(path))

    def walk(self, path, include_deleted=False):
        """
        Walk Directory Contents

        :param str path: Path to walk
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        return io.walk(self._core, self._scope, path, include_deleted=include_deleted)

    def public_link(self, path, access='RO', expire_in=30):
        """
        Create a public link to a file or a folder

        :param str path: The path of the file to create a link to
        :param str,optional access: Access policy of the link, defaults to 'RO'
        :param int,optional expire_in: Number of days until the link expires, defaults to 30
        """
        return io.public_link(self._core, self.normalize(path), access, expire_in)

    def copy(self, *paths, destination=None):
        """
        Copy one or more files or folders

        :param list[str] paths: List of paths
        :param str destination: Destination
        """
        if destination is None:
            raise ValueError('Copy destination was not specified.')
        return io.copy(self._core, *[self.normalize(path) for path in paths], destination=self.normalize(destination))

    def permalink(self, path):
        """
        Get Permalink for Path.

        :param str path: Path.
        """
        p = self.normalize(path)
        contents = [e for e in io.listdir(self._core, p.parent, 1, False, p.name, 1)]  # pylint: disable=unnecessary-comprehension
        if contents and contents[0].name == p.name:
            return contents[0].permalink
        raise FileNotFoundError('File not found.', path)

    def determine_directory_and_filename(self, p, objects=None, destination=None, archive=False):
        """
        Determine location to save file.

        :param str p: Path.
        :param list[str],optional objects: List of files or folders
        :param str,optional destination: Destination
        :param bool,optional archive: Compressed archive
        :returns: Directory and file name
        :rtype: tuple[str]
        """
        directory, name = None, None
        if destination:
            directory, name = self._filesystem.split_file_directory(destination)
        else:
            directory = self._filesystem.downloads_directory()

        if not name:
            normalized = self.normalize(p)
            if archive:
                name = self._filesystem.compute_zip_file_name(normalized.absolute, objects)
            else:
                name = normalized.name
        return directory, name

    def normalize(self, entries):
        return CorePath.instance(self._scope, entries)


class CloudDrive(FileBrowser):

    def upload(self, name, size, destination, handle):
        """
        Upload from file handle.

        :param str name: File name.
        :param str size: File size.
        :param str destination: Path to remote directory.
        :param object handle: Handle.
        """
        upload_function = io.upload(name, size, self.normalize(destination), handle)
        return upload_function(self._core)

    def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path
        :param str destination: Remote path
        """
        with open(path, 'rb') as handle:
            metadata = self._filesystem.properties(path)
            response = self.upload(metadata['name'], metadata['size'], destination, handle)
        return response

    def mkdir(self, path):
        """
        Create a new directory

        :param str path: Directory path
        """
        return io.mkdir(self._core, self.normalize(path))

    def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return io.makedirs(self._core, self.normalize(path))

    def rename(self, path, name):
        """
        Rename a file

        :param str path: Path of the file or directory to rename
        :param str name: The name to rename to
        """
        return io.rename(self._core, self.normalize(path), name)

    def delete(self, *paths):
        """
        Delete one or more files or folders

        :param str path: Path
        """
        return io.remove(self._core, *[self.normalize(path) for path in paths])

    def undelete(self, *paths):
        """
        Recover one or more files or folders

        :param str path: Path
        """
        return io.recover(self._core, *[self.normalize(path) for path in paths])

    def move(self, *paths, destination=None):
        """
        Move one or more files or folders

        :param list[str] paths: List of paths
        :param str destination: Destination
        """
        if destination is None:
            raise ValueError('Move destination was not specified.')
        return io.move(self._core, *[self.normalize(path) for path in paths], destination=self.normalize(destination))

    def get_share_info(self, path):
        """
        Get share settings and recipients

        :param str path: Path
        """
        return io.get_share_info(self._core, self.normalize(path))

    def share(self, path, recipients, as_project=True, allow_reshare=True, allow_sync=True):
        """
        Share a file or a folder

        :param str path: The path of the file or folder to share
        :param list[cterasdk.core.types.ShareRecipient] recipients: A list of share recipients
        :param bool,optional as_project: Share as a team project, defaults to True when the item is a cloud folder else False
        :param bool,optional allow_reshare: Allow recipients to re-share this item, defaults to True
        :param bool,optional allow_sync: Allow recipients to sync this item, defaults to True when the item is a cloud folder else False
        :return: A list of all recipients added to the collaboration share
        :rtype: list[cterasdk.core.types.ShareRecipient]
        """
        return io.share(self._core, self.normalize(path), recipients, as_project, allow_reshare, allow_sync)

    def add_share_recipients(self, path, recipients):
        """
        Add share recipients

        :param str path: The path of the file or folder
        :param list[cterasdk.core.types.ShareRecipient] recipients: A list of share recipients
        :return: A list of all recipients added
        :rtype: list[cterasdk.core.types.ShareRecipient]
        """
        return io.add_share_recipients(self._core, self.normalize(path), recipients)

    def remove_share_recipients(self, path, accounts):
        """
        Remove share recipients

        :param str path: The path of the file or folder
        :param list[cterasdk.core.types.PortalAccount] accounts: A list of portal user or group accounts
        :return: A list of all share recipients removed
        :rtype: list[cterasdk.core.types.PortalAccount]
        """
        return io.remove_share_recipients(self._core, self.normalize(path), accounts)

    def unshare(self, path):
        """
        Unshare a file or a folder
        """
        return io.unshare(self._core, self.normalize(path))


class Backups(FileBrowser):

    def device_config(self, device, destination=None):
        """
        Download a device configuration file

        :param str device: The device name
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        try:
            destination = destination if destination is not None else f'{cterasdk.settings.downloads.location}/{device}.xml'
            return self.download(f'backups/{device}/Device Configuration/db.xml', destination)
        except CTERAException as error:
            logging.getLogger('cterasdk.core').error('Failed downloading configuration file. %s',
                                                     {'device': device, 'error': error.response.reason})
            raise error
