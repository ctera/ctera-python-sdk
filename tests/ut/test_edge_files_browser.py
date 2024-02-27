from unittest import mock
import munch

from cterasdk.edge.files.browser import FileBrowser
from tests.ut import base_edge

import cterasdk.settings


class TestEdgeFilesBrowser(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._files = FileBrowser(self._filer)
        self._path = 'the/quick/brown/fox'
        self._filename = self._path.rsplit('/', maxsplit=1)[-1]
        self._fullpath = '/' + self._path
        self._target = 'target/folder'
        self._target_fullpath = f'/{self._target}/{self._filename}'
        self._default_download_dir = cterasdk.settings.downloads.location
        mock_session = self.patch_call("cterasdk.objects.services.CTERA.session")
        mock_session.return_value = munch.Munch({'update_tenant': lambda x: x})

    def test_download_as_zip_success(self):
        pass  # self._files.download_as_zip()

    def test_upload_success(self):
        pass  # self._files.upload()

    def test_move_dont_overwrite_success(self):
        self._init_webdav()
        self._files.move(self._path, self._target, False)
        self._filer.webdav.move.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath),
                                                 TestEdgeFilesBrowser.make_local_files_dir(self._target_fullpath),
                                                 overwrite=False)

    def test_move_overwrite_success(self):
        self._init_webdav()
        self._files.move(self._path, self._target, True)
        self._filer.webdav.move.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath),
                                                 TestEdgeFilesBrowser.make_local_files_dir(self._target_fullpath),
                                                 overwrite=True)

    def test_copy_dont_overwrite_success(self):
        self._init_webdav()
        self._files.copy(self._path, self._target, False)
        self._filer.webdav.copy.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath),
                                                 TestEdgeFilesBrowser.make_local_files_dir(self._target_fullpath),
                                                 overwrite=False)

    def test_copy_overwrite_success(self):
        self._init_webdav()
        self._files.copy(self._path, self._target, True)
        self._filer.webdav.copy.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath),
                                                 TestEdgeFilesBrowser.make_local_files_dir(self._target_fullpath),
                                                 overwrite=True)

    def test_delete_success(self):
        self._init_webdav()
        self._files.delete(self._path)
        self._filer.webdav.delete.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath))

    def test_mkdir_success(self):
        self._init_webdav()
        self._files.mkdir(self._path)
        self._filer.webdav.mkcol.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath))

    def test_mkdir_recursive_success(self):
        self._init_webdav()
        self._files.makedirs(self._path)
        path = ''
        calls = []
        for item in self._path.split('/'):
            path = path + '/' + item
            calls.append(mock.call(TestEdgeFilesBrowser.make_local_files_dir(path)))
        self._filer.webdav.mkcol.assert_has_calls(calls)

    @staticmethod
    def make_local_files_dir(full_path):
        return full_path
