from .path import CTERAPath
from . import mkdir, rm, file_access


class FileBrowser:
    """ Gateway File Browser APIs """

    def __init__(self, Gateway):
        self._CTERAHost = Gateway
        self._file_access = file_access.FileAccess(Gateway)

    @staticmethod
    def ls(_path):
        return

    def download(self, path, destination=None):
        """
        Download a file

        :param str path: The file's path on the gateway
        :param str,optional destination:
         File destination, if it is a directory, the original filename will be kept, defaults to the default directory
        """
        return self._file_access.download(self.mkpath(path), destination=destination)

    def download_as_zip(self, cloud_directory, files, destination=None):
        """
        Download a list of files and/or directories from a cloud folder as a ZIP file

        .. warning:: The list of files is not validated. The ZIP file will include only the existing  files and directories

        :param str cloud_directory: Path to the cloud directory
        :param list[str] files: List of files and/or directories in the cloud folder to download
        :param str,optional destination:
         File destination, if it is a directory, the filename will be calculated, defaults to the default directory
        """
        self._file_access.download_as_zip(self.mkpath(cloud_directory), files, destination=destination)

    def upload(self, file_path, server_path):
        """
        Upload a file

        :param str file_path: Path to the local file to upload
        :param str server_path: Path to the directory to upload the file to
        """
        self._file_access.upload(file_path, self.mkpath(server_path))

    def mkdir(self, path, recurse=False):
        """
        Create a new directory

        :param str path: The path of the new directory
        :param bool,optional recurse: Create subdirectories if missing, defaults to False
        """
        return mkdir.mkdir(self._CTERAHost, self.mkpath(path), recurse)

    def delete(self, path):
        """
        Delete a file

        :param str path: The file's path on the gateway
        """
        return rm.delete(self._CTERAHost, self.mkpath(path))

    @staticmethod
    def mkpath(path):
        return CTERAPath(path, '/')
