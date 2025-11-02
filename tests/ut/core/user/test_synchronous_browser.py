from unittest import mock
from urllib.parse import quote

from cterasdk.common.object import Object
from cterasdk.core.tasks import AwaitablePortalTask
from tests.ut.core.admin import base_admin


class TestSynchronousFileBrowser(base_admin.BaseCoreTest):
    scope = '/admin/webdav'
    _task_reference = 'servers/MainDB/bgTasks/918908'

    def setUp(self):
        super().setUp()
        self.directory = 'docs'
        self.directory_path = 'a/b c/d'
        self.filename = 'Document.txt'
        self.new_filename = 'Summary.txt'

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

    def test_rename_wait(self):
        self._init_global_admin(execute_response=TestSynchronousFileBrowser._background_task_side_effect)
        ret = self._global_admin.files.rename(f'{self.directory}/{self.filename}', self.new_filename)
        self._global_admin.api.execute.assert_called_once_with('', 'moveResources', mock.ANY)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self.assertEqual(len(actual_param.urls), 1)
        expected_param = TestSynchronousFileBrowser._create_source_dest_parameter(
            f'{self.directory}/{self.filename}',
            f'{self.directory}/{self.new_filename}',
        )
        self.assertEqual(actual_param.urls[0], expected_param[0])
        self.assertEqual(ret, f'{self.directory}/{self.new_filename}')

    def test_rename_no_wait(self):
        self._init_global_admin(execute_response=TestSynchronousFileBrowser._task_reference)
        ret = self._global_admin.files.rename(f'{self.directory}/{self.filename}', self.new_filename, wait=False)
        self.assertEqual(type(ret), AwaitablePortalTask)

    def _create_source_dest_parameter(tuples):
        scope = TestSynchronousFileBrowser.scope
        return [
            Object(**{
                '_classname': 'SrcDstParam',
                'src': f'{scope}/{src}',
                'dst': f'{scope}/{dest}' if dest else None
            })
        for src, dest in tuples]

    def test_delete_wait(self):
        self._init_global_admin(execute_response=TestSynchronousFileBrowser._background_task_side_effect)
        ret = self._global_admin.files.delete(f'{self.directory}/{self.filename}')
        self._global_admin.api.execute.assert_called_once_with('', 'deleteResources', mock.ANY)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self.assertEqual(len(actual_param.urls), 1)
        expected_param = TestSynchronousFileBrowser._create_source_dest_parameter(f'{self.directory}/{self.filename}', None)
        self.assertEqual(actual_param.urls[0], expected_param[0])
        self.assertEqual(ret, [{self.directory}/{self.filename}])

    def test_delete_no_wait(self):
        self._init_global_admin(execute_response=TestSynchronousFileBrowser._task_reference)
        ret = self._global_admin.files.delete(f'{self.directory}/{self.filename}', wait=False)
        self.assertEqual(type(ret), AwaitablePortalTask)

    def test_undelete_wait(self):
        self._init_global_admin(execute_response=TestSynchronousFileBrowser._background_task_side_effect)
        ret = self._global_admin.files.undelete(f'{self.directory}/{self.filename}')
        self._global_admin.api.execute.assert_called_once_with('', 'restoreResources', mock.ANY)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self.assertEqual(len(actual_param.urls), 1)
        expected_param = TestSynchronousFileBrowser._create_source_dest_parameter(f'{self.directory}/{self.filename}', None)
        self.assertEqual(actual_param.urls[0], expected_param[0])
        self.assertEqual(ret, [{self.directory}/{self.filename}])

    def test_undelete_no_wait(self):
        self._init_global_admin(execute_response=TestSynchronousFileBrowser._task_reference)
        ret = self._global_admin.files.undelete(f'{self.directory}/{self.filename}', wait=False)
        self.assertEqual(type(ret), AwaitablePortalTask)

    @staticmethod
    def _background_task_side_effect():
        return mock.MagicMock(side_effect=[
            TestSynchronousFileBrowser._task_reference,
            Object(**{
                '_classname': 'FileManagerBgTask',
                'id': 12345,
                'name': 'Test Task',
                'start_time': '2025-11-02T14:00:00',
                'elapsed_time': 3600,
                'status': 'completed',
                'percentage': 100,
                'end_time': '2025-11-02T15:00:00',
                'result': 'success',
                'progress_str': 'Backup completed successfully',
                'tenant': 'tenant_001',
                'files_processed': 250,
                'bytes_processed': 1073741824,
                'total_files': 250,
                'total_bytes': 1073741824,
                'error_type': None,
                'file_in_progress': None,
                'user_uid': 'user_abc',
                'cursor': 'Test Cursor'
            })
        ])

    """
    def test_move_wait(self):
        m_move = self.patch_call('cterasdk.core.files.io.move')

    def test_move_no_wait(self):
        m_move = self.patch_call('cterasdk.core.files.io.move')

    def test_copy_wait(self):
        m_copy = self.patch_call('cterasdk.core.files.io.copy')

    def test_copy_no_wait(self):
        m_copy = self.patch_call('cterasdk.core.files.io.copy')
    """
