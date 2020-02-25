from .path import CTERAPath
from . import dl, mkdir, rm


class FileBrowser:

    def __init__(self, Gateway):
        self._CTERAHost = Gateway

    @staticmethod
    def ls(_path):
        return

    def download(self, path):
        return dl.download(self._CTERAHost, self.mkpath(path))

    def mkdir(self, path, recurse=False):
        return mkdir.mkdir(self._CTERAHost, self.mkpath(path), recurse)

    def delete(self, path):
        return rm.delete(self._CTERAHost, self.mkpath(path))

    @staticmethod
    def mkpath(path):
        return CTERAPath(path, '/')
