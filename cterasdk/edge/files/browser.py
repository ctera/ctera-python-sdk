from .path import CTERAPath
from . import dl, mkdir, rm


class FileBrowser:
    """ Gateway File Browser APIs """

    def __init__(self, Gateway):
        self._CTERAHost = Gateway

    @staticmethod
    def ls(_path):
        return

    def download(self, path):
        """
        Download a file

        :param str path: The file's path on the gateway
        """
        return dl.download(self._CTERAHost, self.mkpath(path))

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
