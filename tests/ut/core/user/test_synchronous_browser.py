from unittest import mock
from urllib.parse import quote

from cterasdk.common.object import Object
from tests.ut.core.admin import base_admin


class TestSynchronousFileBrowser(base_admin.BaseCoreTest):
    scope = '/admin/webdav'

    def setUp(self):
        super().setUp()
        self.directory = 'docs'
        self.directory_path = 'a/b c/d'
        self.filename = 'Document.txt'

    def test_versions(self):
        response = 'snapshots-response-object'
        self._init_global_admin(execute_response=response)
        ret = self._global_admin.files.versions(self.directory)
        self._global_admin.api.execute.assert_called_once_with('', 'listSnapshots', f'{TestSynchronousFileBrowser.scope}/{self.directory}')
        self.assertEqual(ret, response)

    def test_listdir(self):
        for include_deleted in [True, False]:
            self._init_global_admin(execute_response=Object(**{
                'errorType': None,
                'hasMore': False,
                'items': [self.filename]
            }))
            filename = next(self._global_admin.files.listdir(self.directory, include_deleted=include_deleted))
            self._global_admin.api.execute.assert_called_once_with('', 'fetchResources', mock.ANY)
            param = self._global_admin.api.execute.call_args[0][2]
            self.assertEqual(param.root, f'{TestSynchronousFileBrowser.scope}/{self.directory}')
            self.assertEqual(filename, self.filename)

    def test_mkdir(self):
        self._init_global_admin()
        ret = self._global_admin.files.mkdir(f'{self.directory_path}')
        self._global_admin.api.execute.assert_called_once_with('', 'makeCollection', mock.ANY)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        parts = self.directory_path.split('/')
        parentPath = '/'.join(parts[:-1])
        expected_param = Object(**{
            'name': parts[-1],
            'parentPath': f'{TestSynchronousFileBrowser.scope}/{quote(parentPath)}'
        })
        self._assert_equal_objects(expected_param, actual_param)
        self.assertEqual(ret, self.directory_path)

    def test_makedirs(self):
        self._init_global_admin()
        ret = self._global_admin.files.makedirs(f'{self.directory_path}')
        parts = self.directory_path.split('/')
        self.assertEqual(len(parts), self._global_admin.api.execute.call_count)
        self.assertEqual(ret, self.directory_path)

    """
    def test_rename_wait(self):
        m_rename = self.patch_call('cterasdk.core.files.io.rename')

    def test_rename_no_wait(self):
        m_rename = self.patch_call('cterasdk.core.files.io.rename')

    def test_delete_wait(self):
        m_delete = self.patch_call('cterasdk.core.files.io.delete')

    def test_delete_no_wait(self):
        m_delete = self.patch_call('cterasdk.core.files.io.delete')

    def test_undelete_wait(self):
        m_recover = self.patch_call('cterasdk.core.files.io.recover')

    def test_undelete_no_wait(self):
        m_recover = self.patch_call('cterasdk.core.files.io.recover')

    def test_move_wait(self):
        m_move = self.patch_call('cterasdk.core.files.io.move')

    def test_move_no_wait(self):
        m_move = self.patch_call('cterasdk.core.files.io.move')

    def test_copy_wait(self):
        m_copy = self.patch_call('cterasdk.core.files.io.copy')

    def test_copy_no_wait(self):
        m_copy = self.patch_call('cterasdk.core.files.io.copy')
    """
