from unittest import mock

from cterasdk import config
from cterasdk.edge.files.browser import FileBrowser
from tests.ut import base_edge


class TestEdgeFilesBrowser(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._files = FileBrowser(self._filer)
        self._path = 'the/quick/brown/fox'
        self._filename = self._path.rsplit('/', maxsplit=1)[-1]
        self._fullpath = '/' + self._path
        self._target = 'target/folder'
        self._target_fullpath = f'/{self._target}/{self._filename}'
        self._default_download_dir = config.filesystem['dl']

    def test_download_default_dir_success(self):
        openfile_response = 'Stream'
        self._init_filer(openfile_response=openfile_response)
        mock_save_file = self.patch_call("cterasdk.lib.filesystem.FileSystem.save")
        mock_get_dirpath = self.patch_call("cterasdk.lib.filesystem.FileSystem.get_dirpath",
                                           return_value=self._default_download_dir)
        self._files.download(self._path)
        self._filer.openfile.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath), use_file_url=True)
        mock_get_dirpath.assert_called_once()
        mock_save_file.assert_called_once_with(self._default_download_dir, self._filename, openfile_response)

    def test_openfile_success(self):
        openfile_response = 'Stream'
        self._init_filer(openfile_response=openfile_response)
        ret = self._files.openfile(self._path)
        self._filer.openfile.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath), use_file_url=True)
        self.assertEqual(ret, openfile_response)

    def test_download_as_zip_success(self):
        pass  # self._files.download_as_zip()

    def test_upload_success(self):
        pass  # self._files.upload()

    def test_move_dont_overwrite_success(self):
        self._init_filer()
        self._files.move(self._path, self._target, False)
        self._filer.move.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath),
                                                 TestEdgeFilesBrowser.make_local_files_dir(self._target_fullpath),
                                                 False, use_file_url=True)

    def test_move_overwrite_success(self):
        self._init_filer()
        self._files.move(self._path, self._target, True)
        self._filer.move.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath),
                                                 TestEdgeFilesBrowser.make_local_files_dir(self._target_fullpath),
                                                 True, use_file_url=True)

    def test_copy_dont_overwrite_success(self):
        self._init_filer()
        self._files.copy(self._path, self._target, False)
        self._filer.copy.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath),
                                                 TestEdgeFilesBrowser.make_local_files_dir(self._target_fullpath),
                                                 False, use_file_url=True)

    def test_copy_overwrite_success(self):
        self._init_filer()
        self._files.copy(self._path, self._target, True)
        self._filer.copy.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath),
                                                 TestEdgeFilesBrowser.make_local_files_dir(self._target_fullpath),
                                                 True, use_file_url=True)

    def test_delete_success(self):
        self._filer.rm = mock.MagicMock()
        self._files.delete(self._path)
        self._filer.rm.assert_called_once_with(self._fullpath)

    def test_mkdir_success(self):
        self._init_filer()
        self._files.mkdir(self._path)
        self._filer.mkcol.assert_called_once_with(TestEdgeFilesBrowser.make_local_files_dir(self._fullpath), use_file_url=True)

    def test_mkdir_recursive_success(self):
        self._init_filer()
        self._files.mkdir(self._path, recurse=True)
        path = ''
        calls = []
        for item in self._path.split('/'):
            path = path + '/' + item
            calls.append(mock.call(TestEdgeFilesBrowser.make_local_files_dir(path), use_file_url=True))
        self._filer.mkcol.assert_has_calls(calls)

    @staticmethod
    def make_local_files_dir(full_path):
        return f'localFiles/{full_path}'
