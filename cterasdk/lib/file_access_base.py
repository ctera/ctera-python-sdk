from abc import ABC, abstractmethod

from ..convert import toxmlstr
from .filesystem import FileSystem


class FileAccessBase(ABC):
    def __init__(self, ctera_host):
        self._ctera_host = ctera_host
        self._filesystem = FileSystem.instance()

    def download(self, path):
        dirpath = self._filesystem.get_dirpath()
        handle = self._openfile(path)
        self._filesystem.save(dirpath, path.name(), handle)

    def download_as_zip(self, cloud_directory, files):
        files = files if isinstance(files, list) else [files]
        save_as = self._filesystem.compute_zip_file_name(cloud_directory.fullpath(), files)
        dirpath = self._filesystem.get_dirpath()
        handle = self._get_zip_file_handle(cloud_directory, files)
        self._filesystem.save(dirpath, save_as, handle)

    def upload(self, local_file, dest_path):
        local_file_info = self._filesystem.get_local_file_info(local_file)
        with open(local_file, 'rb') as fd:
            return self._ctera_host.upload(
                self._get_upload_url(dest_path),
                self._get_upload_form(local_file_info, fd, dest_path),
                use_file_url=True
            )

    @abstractmethod
    def _get_upload_url(self, dest_path):
        raise NotImplementedError("Subclass must implement _get_upload_url")

    @abstractmethod
    def _get_upload_form(self, local_file_info, fd, dest_path):
        raise NotImplementedError("Subclass must implement _get_upload_form")

    def _openfile(self, path):
        return self._ctera_host.openfile(self._get_single_file_url(path), use_file_url=True)

    @abstractmethod
    def _get_single_file_url(self, path):
        raise NotImplementedError("Subclass must implement _get_single_file_url")

    def _get_zip_file_handle(self, cloud_directory, files):
        return self._ctera_host.download_zip(
            self._get_multi_file_url(cloud_directory, files),
            self._make_form_data(cloud_directory, files),
            use_file_url=self._use_file_url_for_multi_file_url
        )

    @abstractmethod
    def _get_multi_file_url(self, cloud_directory, files):
        raise NotImplementedError("Subclass must implement _get_multi_file_url")

    @property
    def _use_file_url_for_multi_file_url(self):
        raise NotImplementedError("Subclass must implement _use_file_url_for_multi_file_url")

    def _make_form_data(self, cloud_directory, files):
        return dict(
            inputXML=toxmlstr(self._get_multi_file_object(cloud_directory, files))
        )

    @abstractmethod
    def _get_multi_file_object(self, cloud_directory, files):
        raise NotImplementedError("Subclass must implement _get_multi_file_object")
