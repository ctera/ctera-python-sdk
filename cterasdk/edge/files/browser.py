from ..base_command import BaseCommand
from ...cio.edge import EdgePath
from ...lib import FileSystem
from . import io


class FileBrowser(BaseCommand):
    """ Edge Filer File Browser APIs """

    def __init__(self, edge):
        super().__init__(edge)
        self._filesystem = FileSystem.instance()

    def listdir(self, path):
        """
        List Directory

        :param str path: Path
        """
        return io.listdir(self._edge, path)

    def handle(self, path):
        """
        Get File Handle.

        :param str path: Path to a file
        """
        handle_function = io.handle(self.normalize(path))
        return handle_function(self._edge)

    def handle_many(self, directory, *objects):
        """
        Get a Zip Archive File Handle.

        :param str directory: Path to a folder
        :param args objects: List of files and folders
        """
        handle_many_function = io.handle_many(self.normalize(directory), *objects)
        return handle_many_function(self._edge)

    def download(self, path, destination=None):
        """
        Download a file

        :param str path: The file path on the Edge Filer
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

        :param str target: Path to a directory
        :param list[str] objects: List of files and/or directories in the cloud folder to download
        :param str,optional destination:
         File destination, if it is a directory, the filename will be calculated, defaults to the default directory
        """
        directory, name = self.determine_directory_and_filename(target, objects, destination=destination, archive=True)
        handle = self.handle_many(target, *objects)
        return self._filesystem.save(directory, name, handle)

    def upload(self, name, destination, handle):
        """
        Upload from file handle.

        :param str name: File name.
        :param str destination: Path to remote directory.
        :param object handle: Handle.
        """
        upload_function = io.upload(name, self.normalize(destination), handle)
        return upload_function(self._edge)

    def upload_file(self, path, destination):
        """
        Upload a file.

        :param str path: Local path
        :param str destination: Remote path
        """
        metadata = self._filesystem.properties(path)
        with open(path, 'rb') as handle:
            response = self.upload(metadata['name'], destination, handle)
        return response

    def mkdir(self, path):
        """
        Create a new directory

        :param str path: Directory path
        """
        return io.mkdir(self._edge, self.normalize(path))

    def makedirs(self, path):
        """
        Create a directory recursively

        :param str path: Directory path
        """
        return io.makedirs(self._edge, self.normalize(path))

    def copy(self, path, destination=None, overwrite=False):
        """
        Copy a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        if destination is None:
            raise ValueError('Copy destination was not specified.')
        return io.copy(self._edge, self.normalize(path), self.normalize(destination), overwrite)

    def move(self, path, destination=None, overwrite=False):
        """
        Move a file or a folder

        :param str path: Source file or folder path
        :param str destination: Destination folder path
        :param bool,optional overwrite: Overwrite on conflict, defaults to False
        """
        if destination is None:
            raise ValueError('Move destination was not specified.')
        return io.move(self._edge, self.normalize(path), self.normalize(destination), overwrite)

    def delete(self, path):
        """
        Delete a file

        :param str path: File path
        """
        return io.remove(self._edge, self.normalize(path))

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

    @staticmethod
    def normalize(path):
        return EdgePath('/', path)
