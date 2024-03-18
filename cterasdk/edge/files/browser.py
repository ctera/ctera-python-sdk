from ..base_command import BaseCommand
from . import io, common, file_access


class FileBrowser(BaseCommand):
    """ Edge Filer File Browser APIs """

    def __init__(self, edge):
        super().__init__(edge)
        self._file_access = file_access.FileAccess(edge)

    def download(self, path, destination=None):
        """
        Download a file

        :param str path: The file path on the Edge Filer
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
         File destination, if it is a directory, the filename will be calculated, defaults to the default directory
        """
        return self._file_access.download_as_zip(self.get_object_path(cloud_directory), files, destination=destination)

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
        return io.mkdir(self._edge, self.get_object_path(path))

    def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return io.makedirs(self._edge, self.get_object_path(path))

    def copy(self, path, destination=None, overwrite=False):
        """
        Copy a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        if destination is None:
            raise ValueError('Copy destination was not specified.')
        return io.copy(self._edge, self.get_object_path(path), self.get_object_path(destination), overwrite)

    def move(self, path, destination=None, overwrite=False):
        """
        Move a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        if destination is None:
            raise ValueError('Move destination was not specified.')
        return io.move(self._edge, self.get_object_path(path), self.get_object_path(destination), overwrite)

    def delete(self, path):
        """
        Delete a file

        :param str path: File path
        """
        return io.remove(self._edge, self.get_object_path(path))

    @staticmethod
    def get_object_path(path):
        return common.get_object_path('/', path)
