from .path import CTERAPath

from ..base_command import BaseCommand
from . import ls, directory, rename, rm, recover, mv, cp, ln, file_access


class FileBrowser(BaseCommand):
    """
    Portal File Browser APIs
    """

    def __init__(self, portal, base_path):
        super().__init__(portal)
        self._base_path = base_path
        self._file_access = file_access.FileAccess(portal)

    def ls(self, path):
        """
        Execute ls on the provided path

        :param str path: Path to execute ls on
        """
        return ls.ls(self._portal, self.mkpath(path))

    def walk(self, path):
        """
        Perform walk on the provided path

        :param str path: Path to perform walk on
        """
        paths = [self.mkpath(path)]

        while len(paths) > 0:
            path = paths.pop(0)
            items = ls.ls(self._portal, path)
            for item in items:
                if item.isFolder:
                    paths.append(self.mkpath(item))
                yield item

    def download(self, path):
        """
        Download a file

        :param str path: Path of the file to download
        """
        path = self.mkpath(path)
        self._file_access.download(path)

    def download_as_zip(self, cloud_directory, files):
        """
        Download a list of files and/or directories from a cloud folder as a ZIP file

        .. warning:: The list of files is not validated. The ZIP file will include only the existing  files and directories

        :param str cloud_directory: Path to the cloud directory
        :param list[str] files: List of files and/or directories in the cloud folder to download
        """
        self._file_access.download_as_zip(self.mkpath(cloud_directory), files)

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

        :param str path: Path of the directory to create
        :param bool,optional recurse: Whether to create the path recursivly, defaults to False
        """
        directory.mkdir(self._portal, self.mkpath(path), recurse)

    def rename(self, path, name):
        """
        Rename a file

        :param str path: Path of the file or directory to rename
        :param str name: The name to rename to
        """
        return rename.rename(self._portal, self.mkpath(path), name)

    def delete(self, path):
        """
        Delete a file

        :param str path: Path of the file or directory to delete
        """
        return rm.delete(self._portal, self.mkpath(path))

    def delete_multi(self, *args):
        """
        Delete multiple files and/or directories

        :param `*args`: Variable lengthed list of paths of files and/or directories to delete
        """
        return rm.delete_multi(self._portal, *self.mkpath(list(args)))

    def undelete(self, path):
        """
        Restore a previously deleted file or directory

        :param str path: Path of the file or directory to restore
        """
        return recover.undelete(self._portal, self.mkpath(path))

    def undelete_multi(self, *args):
        """
        Restore previously deleted multiple files and/or directories

        :param `*args`: Variable length list of paths of files and/or directories to restore
        """
        return recover.undelete_multi(self._portal, *self.mkpath(list(args)))

    def move(self, src, dest):
        """
        Move a file or directory

        :param str src: The source path of the file or directory
        :param str dst: The destination path of the file or directory
        """
        return mv.move(self._portal, self.mkpath(src), self.mkpath(dest))

    def move_multi(self, src, dest):
        return mv.move_multi(self._portal, self.mkpath(src), self.mkpath(dest))

    def copy(self, src, dest):
        """
        Copy a file or directory

        :param str src: The source path of the file or directory
        :param str dst: The destination path of the file or directory
        """
        return cp.copy(self._portal, self.mkpath(src), self.mkpath(dest))

    def copy_multi(self, src, dest):
        return cp.copy_multi(self._portal, self.mkpath(src), self.mkpath(dest))

    def mklink(self, path, access='RO', expire_in=30):
        """
        Create a link to a file

        :param str path: The path of the file to create a link to
        :param str,optional access: Access policy of the link, defaults to 'RO'
        :param int,optional expire_in: Number of days until the link expires, defaults to 30
        """
        return ln.mklink(self._portal, self.mkpath(path), access, expire_in)

    def mkpath(self, array):
        if isinstance(array, list):
            return [CTERAPath(item, self._base_path) for item in array]
        return CTERAPath(array, self._base_path)
