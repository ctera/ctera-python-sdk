import logging
from pathlib import Path
from urllib.parse import urljoin
import mimetypes

from ...exception import LocalFileNotFound, RemoteDirectoryNotFound, RemoteFileSystemException, LocalDirectoryNotFound
from .fetch_resources_param import FetchResourcesParamBuilder
from .path import CTERAPath
from ... import config
from ...lib import FileSystem
from ...common import Object
from ...convert import toxmlstr


class FileAccess():
    def __init__(self, ctera_host):
        self._ctera_host = ctera_host

    def upload(self, local_file, dest_path):
        local_file_info = self._get_local_file_info(local_file)
        folder_uid = self._get_folder_uid(dest_path)
        with open(local_file, 'rb') as fd:
            form = dict(
                name=local_file_info['name'],
                Filename=local_file_info['name'],
                fullpath=urljoin(
                    self._ctera_host.base_file_url,
                    CTERAPath(local_file_info['name'], dest_path.fullpath()).encoded_fullpath()
                ),
                fileSize=local_file_info['size'],
                file=(local_file_info['name'], fd, local_file_info['mimetype'][0])
            )
            return self._ctera_host.upload(
                '%s/upload/folders/%s' % (self._ctera_host.context, folder_uid),
                form,
                use_file_url=True
            )

    def download(self, path, save_as):
        handle = self._openfile(path)
        self._save(save_as, handle)

    def download_as_zip(self, cloud_directory, files):
        files = files if isinstance(files, list) else [files]
        save_as = self._compute_zip_file_name(cloud_directory.fullpath(), files)
        handle = self._get_zip_file_handle(cloud_directory, files)
        self._save(save_as, handle)

    def _openfile(self, path):
        logging.getLogger().info('Obtaining file handle. %s', {'path': str(path.relativepath)})
        return self._ctera_host.openfile(path.fullpath(), use_file_url=True)

    def _get_zip_file_handle(self, cloud_directory, files):
        folder_uid = self._get_folder_uid(cloud_directory)
        return self._ctera_host.download_zip(
            '%s/folders/folders/%s' % (self._ctera_host.context, folder_uid),
            self._make_form_data(cloud_directory, files),
            use_file_url=True
        )

    @staticmethod
    def _save(save_as, handle):
        dirpath = config.filesystem['dl']
        try:
            FileSystem.instance().save(dirpath, save_as, handle)
        except LocalDirectoryNotFound as error:
            dirpath = FileSystem.instance().expanduser(dirpath)
            logging.getLogger().error('Download failed. Check the following directory exists. %s', {'path': dirpath})
            if handle is not None:
                handle.close()
            raise error

    @staticmethod
    def _get_local_file_info(local_file):
        path = Path(local_file)
        if not path.exists():
            logging.getLogger().error('The path %(local_file)s was not found', dict(local_file=local_file))
            raise LocalFileNotFound(local_file)
        if not path.is_file():
            logging.getLogger().error('The path %(local_file)s is not not file', dict(local_file=local_file))
            raise LocalFileNotFound(local_file)

        return dict(
            name=path.name,
            size=str(path.stat().st_size),
            mimetype=mimetypes.guess_type(local_file)
        )

    def _get_folder_uid(self, path):
        param = FetchResourcesParamBuilder().root(path.encoded_fullpath()).depth(0).build()
        response = self._ctera_host.execute('', 'fetchResources', param)
        if response.root is None:
            raise RemoteDirectoryNotFound(path.fullpath())
        if not response.root.isFolder:
            raise RemoteFileSystemException('The destination path is not a directory', None, path=path.fullpath())
        return response.root.cloudFolderInfo.uid

    @staticmethod
    def _compute_zip_file_name(cloud_directory, files):
        if len(files) > 1:
            path = Path(cloud_directory)
        else:
            path = Path(files[0])
        return path.stem + '.zip'

    @staticmethod
    def _make_form_data(cloud_directory, files):
        files_obj = Object()
        files_obj.paths = ['/'.join([cloud_directory.fullpath(), filename]) for filename in files]
        files_obj.snapshot = None
        files_obj.password = None
        files_obj.portalName = None
        files_obj.showDeleted = False
        return dict(
            inputXML=toxmlstr(files_obj)
        )
