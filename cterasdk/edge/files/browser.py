from .path import CTERAPath
from . import copy, move, mkdir, rm, file_access
from . import open as openfile


class FileBrowser:
    """ Gateway File Browser APIs """

    def __init__(self, Gateway):
        self._CTERAHost = Gateway
        self._file_access = file_access.FileAccess(Gateway)

    @staticmethod
    def ls(_path):
        return

    def openfile(self, path):
        """
        Obtain a file handle

        :param str path: The file path on the Edge Filer
        """
        return openfile.openfile(self._CTERAHost, self.mkpath(path))

    def download(self, path, destination=None):
        """
        Download a file

        :param str path: The file path on the Edge Filer
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
        return self._file_access.download_as_zip(self.mkpath(cloud_directory), files, destination=destination)

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

    def copy(self, src, dest, overwrite=False):
        """
        Copy a file or a folder

        :param str src: Source file or folder path
        :param str dest: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        return copy.copy(self._CTERAHost, self.mkpath(src), self.mkpath(dest), overwrite)

    def move(self, src, dest, overwrite=False):
        """
        Move a file or a folder

        :param str src: Source file or folder path
        :param str dest: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        return move.move(self._CTERAHost, self.mkpath(src), self.mkpath(dest), overwrite)

    def delete(self, path):
        """
        Delete a file

        :param str path: The file's path on the gateway
        """
        return rm.delete(self._CTERAHost, self.mkpath(path))

    @staticmethod
    def mkpath(path):
        return CTERAPath(path, '/')
