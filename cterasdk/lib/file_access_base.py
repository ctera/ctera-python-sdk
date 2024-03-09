from abc import ABC, abstractmethod

from ..common import utf8_decode
from ..convert import toxmlstr
from .filesystem import FileSystem


class FileAccessBase(ABC):
    def __init__(self, ctera_host):
        self._ctera_host = ctera_host
        self._filesystem = FileSystem.instance()

    def download(self, path, destination=None):
        directory, filename = self._split_destination(destination, path.name)
        handle = self._openfile(path)
        return self._filesystem.save(directory, filename, handle)

    def download_as_zip(self, cloud_directory, files, destination=None):
        files = files if isinstance(files, list) else [files]
        directory, filename = self._split_destination(
            destination,
            self._filesystem.compute_zip_file_name,
            cloud_directory=cloud_directory.fullpath(),
            files=files
        )
        handle = self._get_zip_file_handle(cloud_directory, files)
        return self._filesystem.save(directory, filename, handle)

    def upload(self, local_file, dest_path):
        local_file_info = self._filesystem.get_local_file_info(local_file)
        with open(local_file, 'rb') as fd:
            return self._upload_object(local_file_info, fd, dest_path)

    @abstractmethod
    def _upload_object(self, local_file_info, fd, dest_path):
        raise NotImplementedError("Subclass must implement _upload_object")

    @abstractmethod
    def _get_upload_url(self, dest_path):
        raise NotImplementedError("Subclass must implement _get_upload_url")

    @abstractmethod
    def _get_upload_form(self, local_file_info, fd, dest_path):
        raise NotImplementedError("Subclass must implement _get_upload_form")

    def _openfile(self, path):
        return self._ctera_host.io.download(self._get_single_file_url(path))

    @abstractmethod
    def _get_single_file_url(self, path):
        raise NotImplementedError("Subclass must implement _get_single_file_url")

    def _get_zip_file_handle(self, cloud_directory, files):
        raise NotImplementedError("Subclass must implement _get_zip_file_handle")

    @abstractmethod
    def _get_multi_file_url(self, cloud_directory, files):
        raise NotImplementedError("Subclass must implement _get_multi_file_url")

    @property
    def _use_file_url_for_multi_file_url(self):
        raise NotImplementedError("Subclass must implement _use_file_url_for_multi_file_url")

    def _make_form_data(self, cloud_directory, files):
        return dict(
            inputXML=utf8_decode(toxmlstr(self._get_multi_file_object(cloud_directory, files)))
        )

    @abstractmethod
    def _get_multi_file_object(self, cloud_directory, files):
        raise NotImplementedError("Subclass must implement _get_multi_file_object")

    def _split_destination(self, destination, filename_resolver, **filename_resolver_kwargs):
        directory = filename = None
        if destination:
            directory, filename = self._filesystem.split_file_directory(destination)
        else:
            directory = self._filesystem.get_dirpath()
        if filename is None:
            filename = filename_resolver(**filename_resolver_kwargs)
        return directory, filename
