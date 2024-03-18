from ...common import Object
from ...lib import FileAccessBase


class FileAccess(FileAccessBase):

    def _get_single_file_url(self, path):
        return path.fullpath()

    def _get_multi_file_url(self, cloud_directory, files):
        return '/admingui/api/status/fileManager/zip'

    @property
    def _use_file_url_for_multi_file_url(self):
        return False

    def _get_multi_file_object(self, cloud_directory, files):
        files_obj = Object()
        files_obj.paths = ['/'.join([cloud_directory.fullpath(), filename]) for filename in files]
        files_obj.snapshot = Object()
        files_obj._classname = 'BackupRepository'  # pylint: disable=protected-access
        files_obj.snapshot.location = 1
        files_obj.snapshot.timestamp = None
        files_obj.snapshot.path = None
        return files_obj

    def _get_upload_url(self, dest_path):
        return '/actions/upload'

    def _get_upload_form(self, local_file_info, fd, dest_path):
        return dict(
            name=local_file_info['name'],
            fullpath=f'{dest_path.fullpath()}/{local_file_info["name"]}',
            filedata=fd
        )

    def _get_zip_file_handle(self, cloud_directory, files):
        return self._ctera_host.io.download_zip(
            self._get_multi_file_url(cloud_directory, files),
            self._make_form_data(cloud_directory, files)
        )

    def _upload_object(self, local_file_info, fd, dest_path):
        return self._ctera_host.io.upload(
                self._get_upload_url(dest_path),
                self._get_upload_form(local_file_info, fd, dest_path)
            )
