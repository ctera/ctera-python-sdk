import munch
from unittest import mock

from cterasdk.common.object import Object
from cterasdk.core.files.browser import CloudDrive
from tests.ut.core.admin import base_admin


class TestSynchronousFileBrowser(base_admin.BaseCoreTest):
    scope = '/admin/webdav'

    def setUp(self):
        super().setUp()
        self.files = CloudDrive(self._global_admin)
        self.directory = 'docs'
        self.filename = 'Document.txt'

    def test_versions(self):
        response = 'snapshots-response-object'
        self._init_global_admin(execute_response=response)
        ret = self.files.versions(self.directory)
        self._global_admin.api.execute.assert_called_once_with('', 'listSnapshots', f'{TestSynchronousFileBrowser.scope}/{self.directory}')
        self.assertEqual(ret, response)

    def test_listdir(self):
        for include_deleted in [True, False]:
            self._init_global_admin(execute_response=self._create_fetch_resources_response_object())
            filename = next(self.files.listdir(self.directory, include_deleted=include_deleted))
            self._global_admin.api.execute.assert_called_once_with('', 'fetchResources', mock.ANY)
            param = self._global_admin.api.execute.call_args[0][2]
            self.assertEqual(param.root, f'{TestSynchronousFileBrowser.scope}/{self.directory}')
            self.assertEqual(filename, self.filename)

    def _create_fetch_resources_response_object(self):
        return Object(**{
            'errorType': None,
            'hasMore': False,
            'items': [self.filename]
        })
    """
    def test_mkdir(self):
        m_mkdir = self.patch_call('cterasdk.core.files.io.mkdir')

    def test_makedirs(self):
        m_makedirs = self.patch_call('cterasdk.core.files.io.makedirs')

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
