
from . import io
from ...cio.core import CorePath
from ...common import Object
from ...lib import FileAccessBase
from ...cio import exceptions


class FileAccess(FileAccessBase):

    def _get_single_file_url(self, path):
        return path.reference

    def _get_multi_file_url(self, cloud_directory, files):
        return str(self._get_cloud_folder_uid(cloud_directory))

    @property
    def _use_file_url_for_multi_file_url(self):
        return True

    def _get_multi_file_object(self, cloud_directory, files):
        files_obj = Object()
        files_obj.paths = ['/'.join([cloud_directory.absolute, filename]) for filename in files]
        files_obj.snapshot = None
        files_obj.password = None
        files_obj.portalName = None
        files_obj.showDeleted = False
        return files_obj

    def _get_upload_url(self, dest_path):
        return str(self._get_cloud_folder_uid(dest_path))

    def _get_upload_form(self, local_file_info, fd, dest_path):
        return dict(
            name=local_file_info['name'],
            Filename=local_file_info['name'],
            fullpath=self._ctera_host.io.builder(CorePath(dest_path.reference,  # pylint: disable=protected-access
                                                          local_file_info['name']).absolute_encode),
                                                          fileSize=local_file_info['size'],
                                                          file=fd
            )

    def _get_cloud_folder_uid(self, path):
        resource_info = io.root(self._ctera_host, path)
        if not resource_info.isFolder:
            raise exceptions.RemoteStorageException('The destination path is not a directory', None, path=path.absolute)
        return resource_info.cloudFolderInfo.uid

    def _get_zip_file_handle(self, cloud_directory, files):
        return self._ctera_host.io.download_zip(  # pylint: disable=protected-access
            self._get_multi_file_url(cloud_directory, files),
            self._make_form_data(cloud_directory, files)
        )

    def _upload_object(self, local_file_info, fd, dest_path):
        return self._ctera_host.io.upload(  # pylint: disable=protected-access
                self._get_upload_url(dest_path),
                self._get_upload_form(local_file_info, fd, dest_path)
            )
