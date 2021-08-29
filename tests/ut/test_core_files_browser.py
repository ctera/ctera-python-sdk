import os
from unittest import mock

from cterasdk.core.files.browser import CloudDrive
from tests.ut import base_core


class TestCoreFilesBrowser(base_core.BaseCoreTest):
    _base_path = '/admin/webdav/Users'

    def setUp(self):
        super().setUp()
        self.files = CloudDrive(self._global_admin, TestCoreFilesBrowser._base_path)

    def test_ls(self):
        path = 'cloud/Users'
        ls_mock = self.patch_call('cterasdk.core.files.browser.ls')
        self.files.ls(path)
        ls_mock.ls.assert_called_once_with(self._global_admin, mock.ANY, include_deleted=False)
        actual_ctera_path = ls_mock.ls.call_args[0][1]
        self.assertEqual(actual_ctera_path.fullpath(), os.path.join(TestCoreFilesBrowser._base_path, path))

    def test_ls_deleted_files(self):
        path = 'cloud/Users'
        ls_mock = self.patch_call('cterasdk.core.files.browser.ls')
        self.files.ls(path, True)
        ls_mock.ls.assert_called_once_with(self._global_admin, mock.ANY, include_deleted=True)
        actual_ctera_path = ls_mock.ls.call_args[0][1]
        self.assertEqual(actual_ctera_path.fullpath(), os.path.join(TestCoreFilesBrowser._base_path, path))

    def test_mkdir(self):
        for recurse in [True, False]:
            self._test_mkdir(recurse)

    def _test_mkdir(self, recurse):
        path = 'cloud/Users'
        directory_mock = self.patch_call('cterasdk.core.files.browser.directory')
        self.files.mkdir(path, recurse=recurse)
        directory_mock.mkdir.assert_called_once_with(self._global_admin, mock.ANY, recurse)
        actual_ctera_path = directory_mock.mkdir.call_args[0][1]
        self.assertEqual(actual_ctera_path.fullpath(), os.path.join(TestCoreFilesBrowser._base_path, path))

    def test_rename(self):
        path = 'cloud/Users'
        new_name = 'Names'
        rename_mock = self.patch_call('cterasdk.core.files.browser.rename')
        self.files.rename(path, new_name)
        rename_mock.rename.assert_called_once_with(self._global_admin, mock.ANY, new_name)
        actual_ctera_path = rename_mock.rename.call_args[0][1]
        self.assertEqual(actual_ctera_path.fullpath(), os.path.join(TestCoreFilesBrowser._base_path, path))

    def test_delete(self):
        path = 'cloud/Users'
        rm_mock = self.patch_call('cterasdk.core.files.browser.rm')
        self.files.delete(path)
        rm_mock.delete.assert_called_once_with(self._global_admin, mock.ANY)
        actual_ctera_path = rm_mock.delete.call_args[0][1]
        self.assertEqual(actual_ctera_path.fullpath(), os.path.join(TestCoreFilesBrowser._base_path, path))

    def test_delete_multi(self):
        paths = ['cloud/Users', 'public']
        rm_mock = self.patch_call('cterasdk.core.files.browser.rm')
        self.files.delete_multi(*paths)
        rm_mock.delete_multi.assert_called_once_with(self._global_admin, mock.ANY, mock.ANY)
        actual_ctera_paths = rm_mock.delete_multi.call_args[0][1:]
        self.assertListEqual(
            [actual_ctera_path.fullpath() for actual_ctera_path in actual_ctera_paths],
            [os.path.join(TestCoreFilesBrowser._base_path, path) for path in paths]
        )

    def test_undelete(self):
        path = 'cloud/Users'
        recover_mock = self.patch_call('cterasdk.core.files.browser.recover')
        self.files.undelete(path)
        recover_mock.undelete.assert_called_once_with(self._global_admin, mock.ANY)
        actual_ctera_path = recover_mock.undelete.call_args[0][1]
        self.assertEqual(actual_ctera_path.fullpath(), os.path.join(TestCoreFilesBrowser._base_path, path))

    def test_undelete_multi(self):
        paths = ['cloud/Users', 'public']
        recover_mock = self.patch_call('cterasdk.core.files.browser.recover')
        self.files.undelete_multi(*paths)
        recover_mock.undelete_multi.assert_called_once_with(self._global_admin, mock.ANY, mock.ANY)
        actual_ctera_paths = recover_mock.undelete_multi.call_args[0][1:]
        self.assertListEqual(
            [actual_ctera_path.fullpath() for actual_ctera_path in actual_ctera_paths],
            [os.path.join(TestCoreFilesBrowser._base_path, path) for path in paths]
        )

    def test_move(self):
        src = 'cloud/Users'
        dst = 'public'
        mv_mock = self.patch_call('cterasdk.core.files.browser.mv')
        self.files.move(src, dst)
        mv_mock.move.assert_called_once_with(self._global_admin, mock.ANY, mock.ANY)
        actual_ctera_paths = mv_mock.move.call_args[0][1:]
        self.assertListEqual(
            [actual_ctera_path.fullpath() for actual_ctera_path in actual_ctera_paths],
            [os.path.join(TestCoreFilesBrowser._base_path, path) for path in [src, dst]]
        )

    def test_move_multi(self):
        src = 'cloud/Users'
        dst = 'public'
        mv_mock = self.patch_call('cterasdk.core.files.browser.mv')
        self.files.move_multi(src, dst)
        mv_mock.move_multi.assert_called_once_with(self._global_admin, mock.ANY, mock.ANY)
        actual_ctera_paths = mv_mock.move_multi.call_args[0][1:]
        self.assertListEqual(
            [actual_ctera_path.fullpath() for actual_ctera_path in actual_ctera_paths],
            [os.path.join(TestCoreFilesBrowser._base_path, path) for path in [src, dst]]
        )

    def test_copy(self):
        src = 'cloud/Users'
        dst = 'public'
        cp_mock = self.patch_call('cterasdk.core.files.browser.cp')
        self.files.copy(src, dst)
        cp_mock.copy.assert_called_once_with(self._global_admin, mock.ANY, mock.ANY)
        actual_ctera_paths = cp_mock.copy.call_args[0][1:]
        self.assertListEqual(
            [actual_ctera_path.fullpath() for actual_ctera_path in actual_ctera_paths],
            [os.path.join(TestCoreFilesBrowser._base_path, path) for path in [src, dst]]
        )

    def test_copy_multi(self):
        src = 'cloud/Users'
        dst = 'public'
        cp_mock = self.patch_call('cterasdk.core.files.browser.cp')
        self.files.copy_multi(src, dst)
        cp_mock.copy_multi.assert_called_once_with(self._global_admin, mock.ANY, mock.ANY)
        actual_ctera_paths = cp_mock.copy_multi.call_args[0][1:]
        self.assertListEqual(
            [actual_ctera_path.fullpath() for actual_ctera_path in actual_ctera_paths],
            [os.path.join(TestCoreFilesBrowser._base_path, path) for path in [src, dst]]
        )

    def test_mklink_default_values(self):
        for access in [None, 'RW', 'RO']:
            for expire_in in [None, 15, 30, 0]:
                params = dict()
                if access is not None:
                    params['access'] = access
                if expire_in is not None:
                    params['expire_in'] = expire_in
                self._test_mklink(**params)

    def _test_mklink(self, access=None, expire_in=None):
        mklink_args = dict(
            path='cloud/Users'
        )
        if access is not None:
            mklink_args['access'] = access
        if expire_in is not None:
            mklink_args['expire_in'] = expire_in
        ln_mock = self.patch_call('cterasdk.core.files.browser.ln')
        self.files.mklink(**mklink_args)
        ln_mock.mklink.assert_called_once_with(
            self._global_admin,
            mock.ANY,
            access if access is not None else 'RO',
            expire_in if expire_in is not None else 30
        )
        actual_ctera_path = ln_mock.mklink.call_args[0][1]
        self.assertEqual(actual_ctera_path.fullpath(), os.path.join(TestCoreFilesBrowser._base_path, mklink_args['path']))
