import logging

import cterasdk.settings
from ...exceptions import CTERAException
from ..base_command import BaseCommand
from . import io, common, shares, file_access


class FileBrowser(BaseCommand):

    def __init__(self, core):
        super().__init__(core)
        self._base = f'/{self._core.context}/webdav'
        self._file_access = file_access.FileAccess(self._core)

    def download(self, path, destination=None):
        """
        Download a file

        :param str path: Path
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        return self._file_access.download(self.get_object_path(path), destination=destination)

    def download_as_zip(self, cloud_directory, files, destination=None):
        """
        Download a list of files and/or directories from a cloud folder as a ZIP file

        .. warning:: The list of files is not validated. The ZIP file will include only the existing  files and directories

        :param str cloud_directory: Path to the cloud directory
        :param list[str] files: List of files and/or directories in the cloud folder to download
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        self._file_access.download_as_zip(self.get_object_path(cloud_directory), files, destination=destination)

    def listdir(self, path, depth=None, include_deleted=False):
        """
        List Directory

        :param str path: Path
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        return io.listdir(self._core, self.get_object_path(path), depth=depth, include_deleted=include_deleted)

    def walk(self, path, include_deleted=False):
        """
        Walk Directory Contents

        :param str path: Path to walk
        :param bool,optional include_deleted: Include deleted files, defaults to False
        """
        return io.walk(self._core, self._base, path, include_deleted=include_deleted)

    def public_link(self, path, access='RO', expire_in=30):
        """
        Create a public link to a file or a folder

        :param str path: The path of the file to create a link to
        :param str,optional access: Access policy of the link, defaults to 'RO'
        :param int,optional expire_in: Number of days until the link expires, defaults to 30
        """
        return shares.create_public_link(self._core, self.get_object_path(path), access, expire_in)

    def copy(self, *paths, destination=None):
        """
        Copy one or more files or folders

        :param list[str] paths: List of paths
        :param str destination: Destination
        """
        if destination is None:
            raise ValueError('Copy destination was not specified.')
        return io.copy(self._core, *[self.get_object_path(path) for path in paths], destination=self.get_object_path(destination))

    def get_object_path(self, elements):
        return common.get_object_path(self.base, elements)

    @property
    def base(self):
        return self._base


class CloudDrive(FileBrowser):

    def upload(self, path, destination):
        """
        Upload a file

        :param str path: Local path
        :param str destination: Remote path
        """
        self._file_access.upload(path, self.get_object_path(destination))

    def mkdir(self, path):
        """
        Create a new directory

        :param str path: Directory path
        """
        return io.mkdir(self._core, self.get_object_path(path))

    def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return io.makedirs(self._core, self.get_object_path(path))

    def rename(self, path, name):
        """
        Rename a file

        :param str path: Path of the file or directory to rename
        :param str name: The name to rename to
        """
        return io.rename(self._core, self.get_object_path(path), name)

    def delete(self, *paths):
        """
        Delete one or more files or folders

        :param str path: Path
        """
        return io.remove(self._core, *[self.get_object_path(path) for path in paths])

    def undelete(self, *paths):
        """
        Recover one or more files or folders

        :param str path: Path
        """
        return io.recover(self._core, *[self.get_object_path(path) for path in paths])

    def move(self, *paths, destination=None):
        """
        Move one or more files or folders

        :param list[str] paths: List of paths
        :param str destination: Destination
        """
        if destination is None:
            raise ValueError('Move destination was not specified.')
        return io.move(self._core, *[self.get_object_path(path) for path in paths], destination=self.get_object_path(destination))

    def get_share_info(self, path):
        """
        Get share settings and recipients

        :param str path: Path
        """
        return shares.get_share_info(self._core, self.get_object_path(path))

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
        return shares.share(self._core, self.get_object_path(path), recipients, as_project, allow_reshare, allow_sync)

    def add_share_recipients(self, path, recipients):
        """
        Add share recipients

        :param str path: The path of the file or folder
        :param list[cterasdk.core.types.ShareRecipient] recipients: A list of share recipients
        :return: A list of all recipients added
        :rtype: list[cterasdk.core.types.ShareRecipient]
        """
        return shares.add_share_recipients(self._core, self.get_object_path(path), recipients)

    def remove_share_recipients(self, path, accounts):
        """
        Remove share recipients

        :param str path: The path of the file or folder
        :param list[cterasdk.core.types.PortalAccount] accounts: A list of portal user or group accounts
        :return: A list of all share recipients removed
        :rtype: list[cterasdk.core.types.PortalAccount]
        """
        return shares.remove_share_recipients(self._core, self.get_object_path(path), accounts)

    def unshare(self, path):
        """
        Unshare a file or a folder
        """
        return shares.unshare(self._core, self.get_object_path(path))


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

    @property
    def base(self):
        return f'{super().base}/backups'
