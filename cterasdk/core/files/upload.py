import logging
from pathlib import Path
from urllib.parse import urljoin
import mimetypes

from ...exception import LocalFileNotFound, RemoteDirectoryNotFound, RemoteFileSystemException
from .fetch_resources_param import FetchResourcesParamBuilder
from .path import CTERAPath


class CoreUpload():
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

    def _get_folder_uid(self, dest_path):
        param = FetchResourcesParamBuilder().root(dest_path.encoded_fullpath()).depth(0).build()
        response = self._ctera_host.execute('', 'fetchResources', param)
        if response.root is None:
            raise RemoteDirectoryNotFound(dest_path.fullpath())
        if not response.root.isFolder:
            raise RemoteFileSystemException('The destination path is not a directory', None, path=dest_path.fullpath())
        return response.root.cloudFolderInfo.uid


def upload(ctera_host, local_file, dest_path):
    return CoreUpload(ctera_host).upload(local_file, dest_path)
