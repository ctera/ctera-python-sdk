from urllib.parse import urljoin

from .path import CTERAPath
from . import common
from ...common import Object
from ...lib import FileAccessBase
from ...exception import RemoteFileSystemException


class FileAccess(FileAccessBase):

    def _get_single_file_url(self, path):
        return path.fullpath()

    def _get_multi_file_url(self, cloud_directory, files):
        folder_uid = self._get_cloud_folder_uid(cloud_directory)
        return '%s/folders/folders/%s' % (self._ctera_host.context, folder_uid)

    @property
    def _use_file_url_for_multi_file_url(self):
        return True

    def _get_multi_file_object(self, cloud_directory, files):
        files_obj = Object()
        files_obj.paths = ['/'.join([cloud_directory.fullpath(), filename]) for filename in files]
        files_obj.snapshot = None
        files_obj.password = None
        files_obj.portalName = None
        files_obj.showDeleted = False
        return files_obj

    def _get_upload_url(self, dest_path):
        folder_uid = self._get_cloud_folder_uid(dest_path)
        return '%s/upload/folders/%s' % (self._ctera_host.context, folder_uid)

    def _get_upload_form(self, local_file_info, fd, dest_path):
        return dict(
            name=local_file_info['name'],
            Filename=local_file_info['name'],
            fullpath=urljoin(
                self._ctera_host.base_file_url,
                CTERAPath(local_file_info['name'], dest_path.fullpath()).encoded_fullpath()
            ),
            fileSize=local_file_info['size'],
            file=(local_file_info['name'], fd, local_file_info['mimetype'][0])
        )

    def _get_cloud_folder_uid(self, path):
        resource_info = common.get_resource_info(self._ctera_host, path)
        if not resource_info.isFolder:
            raise RemoteFileSystemException('The destination path is not a directory', None, path=path.fullpath())
        return resource_info.cloudFolderInfo.uid
