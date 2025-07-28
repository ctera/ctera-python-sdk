from unittest import mock
from pathlib import Path

from cterasdk.core.files.browser import CloudDrive
from tests.ut.core.admin import base_admin


class TestCoreFilesBrowser(base_admin.BaseCoreTest):
    _base_path = '/admin/webdav'

    def setUp(self):
        super().setUp()
        self.files = CloudDrive(self._global_admin)

    def test_versions(self):
        path = 'cloud/Users'
        versions_mock = self.patch_call('cterasdk.core.files.io.versions')
        self.files.versions(path)
        versions_mock.assert_called_once_with(self._global_admin, mock.ANY)
        actual_ctera_path = versions_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path))

    def test_listdir(self):
        path = 'cloud/Users'
        listdir_mock = self.patch_call('cterasdk.core.files.io.listdir')
        self.files.listdir(path)
        listdir_mock.assert_called_once_with(self._global_admin, mock.ANY, depth=None, include_deleted=False)
        actual_ctera_path = listdir_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path))

    def test_listdir_deleted_files(self):
        path = 'cloud/Users'
        listdir_mock = self.patch_call('cterasdk.core.files.io.listdir')
        self.files.listdir(path, include_deleted=True)
        listdir_mock.assert_called_once_with(self._global_admin, mock.ANY, depth=None, include_deleted=True)
        actual_ctera_path = listdir_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path))

    def test_mkdir(self):
        path = 'cloud/Users'
        mkdir_mock = self.patch_call('cterasdk.core.files.io.mkdir')
        self.files.mkdir(path)
        mkdir_mock.assert_called_once_with(self._global_admin, mock.ANY)
        actual_ctera_path = mkdir_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path))

    def test_makedirs(self):
        path = 'cloud/Users'
        makedirs_mock = self.patch_call('cterasdk.core.files.io.makedirs')
        self.files.makedirs(path)
        makedirs_mock.assert_called_once_with(self._global_admin, mock.ANY)
        actual_ctera_path = makedirs_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path))

    def test_rename(self):
        path = 'cloud/Users'
        new_name = 'Names'
        rename_mock = self.patch_call('cterasdk.core.files.io.rename')
        self.files.rename(path, new_name)
        rename_mock.assert_called_once_with(self._global_admin, mock.ANY, new_name, wait=True)
        actual_ctera_path = rename_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path))

    def test_delete(self):
        path = 'cloud/Users'
        rm_mock = self.patch_call('cterasdk.core.files.io.remove')
        self.files.delete(path)
        rm_mock.assert_called_once_with(self._global_admin, mock.ANY, wait=True)
        actual_ctera_path = rm_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path))

    def test_undelete(self):
        path = 'cloud/Users'
        recover_mock = self.patch_call('cterasdk.core.files.io.recover')
        self.files.undelete(path)
        recover_mock.assert_called_once_with(self._global_admin, mock.ANY, wait=True)
        actual_ctera_path = recover_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path))

    def test_move(self):
        src = 'cloud/Users'
        dst = 'public'
        mv_mock = self.patch_call('cterasdk.core.files.io.move')
        self.files.move(src, destination=dst)
        mv_mock.assert_called_once_with(self._global_admin, mock.ANY, destination=mock.ANY, wait=True)
        actual_ctera_paths = mv_mock.call_args[0][1:]
        self.assertListEqual(
            [actual_ctera_path.absolute for actual_ctera_path in actual_ctera_paths],
            [TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path) for path in [src]]
        )

    def test_copy(self):
        src = 'cloud/Users'
        dst = 'public'
        cp_mock = self.patch_call('cterasdk.core.files.io.copy')
        self.files.copy(src, destination=dst)
        cp_mock.assert_called_once_with(self._global_admin, mock.ANY, destination=mock.ANY, wait=True)
        actual_ctera_paths = cp_mock.call_args[0][1:]
        self.assertListEqual(
            [actual_ctera_path.absolute for actual_ctera_path in actual_ctera_paths],
            [TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path, path) for path in [src]]
        )

    def test_create_public_link_default_values(self):
        for access in [None, 'RW', 'RO']:
            for expire_in in [None, 15, 30, 0]:
                params = {}
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
        ln_mock = self.patch_call('cterasdk.core.files.io.public_link')
        self.files.public_link(**mklink_args)
        ln_mock.assert_called_once_with(
            self._global_admin,
            mock.ANY,
            access if access is not None else 'RO',
            expire_in if expire_in is not None else 30
        )
        actual_ctera_path = ln_mock.call_args[0][1]
        self.assertEqual(actual_ctera_path.absolute, TestCoreFilesBrowser._create_expected_path(TestCoreFilesBrowser._base_path,
                                                                                                mklink_args['path']))

    @staticmethod
    def _create_expected_path(base, path):
        return Path(base).joinpath(path).as_posix()
