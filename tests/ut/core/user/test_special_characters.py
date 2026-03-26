from unittest import mock
from urllib.parse import quote
from datetime import datetime

import munch

from cterasdk.common import Object
from tests.ut.core.user import base_user


class TestSpecialCharacterPaths(base_user.BaseCoreServicesTest):
    """
    PIM-6659: Verify that all file operations properly URL-encode paths
    containing special characters (%, #, spaces, etc.) when constructing
    WebDAV or API request parameters.
    """

    SPECIAL_FILENAMES = [
        'file_100%_done.txt',
        'file_%25_encoded.txt',
        'report #1.txt',
        'file with spaces.txt',
        'file_!@#$%^([{.txt',
        'résumé.txt',
    ]

    SPECIAL_DIRECTORIES = [
        'My Files/Documents 2026',
        'My Files/100% Complete',
        'My Files/Report #1',
    ]

    def setUp(self):
        super().setUp()
        self._special_dir = 'My Files/100% Complete'
        self._special_filename = 'file_100%_done.txt'
        self._special_path = f'{self._special_dir}/{self._special_filename}'

    def _expected_encoded_absolute(self, path):
        return f'{self._base}/{quote(path)}'

    # --- Open / handle ---

    def test_handle_encodes_special_characters(self):
        for filename in self.SPECIAL_FILENAMES:
            path = f'My Files/{filename}'
            self._init_services()
            mock_download = mock.MagicMock()
            self._services.io._webdav.download = mock_download  # pylint: disable=protected-access
            self._services.files.handle(path)
            call_args = mock_download.call_args[0]
            actual_path = str(call_args[0])
            expected_path = quote(f'My Files/{filename}')
            self.assertEqual(actual_path, expected_path,
                             f'handle() did not encode path for filename: {filename}')

    def test_handle_percent_in_directory(self):
        for directory in self.SPECIAL_DIRECTORIES:
            path = f'{directory}/document.txt'
            self._init_services()
            mock_download = mock.MagicMock()
            self._services.io._webdav.download = mock_download  # pylint: disable=protected-access
            self._services.files.handle(path)
            call_args = mock_download.call_args[0]
            actual_path = str(call_args[0])
            expected_path = quote(path)
            self.assertEqual(actual_path, expected_path,
                             f'handle() did not encode directory: {directory}')

    # --- Delete ---

    def test_delete_encodes_special_characters(self):
        for filename in self.SPECIAL_FILENAMES:
            path = f'My Files/{filename}'
            self._init_services(execute_response=self._task_reference)
            self._services.files.delete(path, wait=False)
            self._services.api.execute.assert_called_once_with('', 'deleteResources', mock.ANY)
            actual_param = self._services.api.execute.call_args[0][2]
            self.assertEqual(actual_param.urls[0].src, self._expected_encoded_absolute(path),
                             f'delete() did not encode path for filename: {filename}')

    # --- Undelete / Recover ---

    def test_undelete_encodes_special_characters(self):
        for filename in self.SPECIAL_FILENAMES:
            path = f'My Files/{filename}'
            self._init_services(execute_response=self._task_reference)
            self._services.files.undelete(path, wait=False)
            self._services.api.execute.assert_called_once_with('', 'restoreResources', mock.ANY)
            actual_param = self._services.api.execute.call_args[0][2]
            self.assertEqual(actual_param.urls[0].src, self._expected_encoded_absolute(path),
                             f'undelete() did not encode path for filename: {filename}')

    # --- Copy ---

    def test_copy_encodes_special_characters(self):
        for filename in self.SPECIAL_FILENAMES:
            source = f'My Files/{filename}'
            dest_dir = 'My Files/Archive'
            self._init_services(execute_response=self._task_reference)
            self._services.files.copy(source, destination=dest_dir, wait=False)
            self._services.api.execute.assert_called_once_with('', 'copyResources', mock.ANY)
            actual_param = self._services.api.execute.call_args[0][2]
            self.assertEqual(actual_param.urls[0].src, self._expected_encoded_absolute(source),
                             f'copy() did not encode source for filename: {filename}')
            expected_dest = self._expected_encoded_absolute(f'{dest_dir}/{filename}')
            self.assertEqual(actual_param.urls[0].dest, expected_dest,
                             f'copy() did not encode dest for filename: {filename}')

    def test_copy_to_special_char_destination(self):
        source = 'My Files/document.txt'
        dest_dir = 'My Files/100% Complete'
        self._init_services(execute_response=self._task_reference)
        self._services.files.copy(source, destination=dest_dir, wait=False)
        actual_param = self._services.api.execute.call_args[0][2]
        expected_dest = self._expected_encoded_absolute(f'{dest_dir}/document.txt')
        self.assertEqual(actual_param.urls[0].dest, expected_dest)

    # --- Move ---

    def test_move_encodes_special_characters(self):
        for filename in self.SPECIAL_FILENAMES:
            source = f'My Files/{filename}'
            dest_dir = 'My Files/Archive'
            self._init_services(execute_response=self._task_reference)
            self._services.files.move(source, destination=dest_dir, wait=False)
            self._services.api.execute.assert_called_once_with('', 'moveResources', mock.ANY)
            actual_param = self._services.api.execute.call_args[0][2]
            self.assertEqual(actual_param.urls[0].src, self._expected_encoded_absolute(source),
                             f'move() did not encode source for filename: {filename}')
            expected_dest = self._expected_encoded_absolute(f'{dest_dir}/{filename}')
            self.assertEqual(actual_param.urls[0].dest, expected_dest,
                             f'move() did not encode dest for filename: {filename}')

    def test_move_from_special_char_directory(self):
        source = 'My Files/100% Complete/document.txt'
        dest_dir = 'My Files/Archive'
        self._init_services(execute_response=self._task_reference)
        self._services.files.move(source, destination=dest_dir, wait=False)
        actual_param = self._services.api.execute.call_args[0][2]
        self.assertEqual(actual_param.urls[0].src, self._expected_encoded_absolute(source))

    # --- Rename ---

    def test_rename_encodes_special_characters(self):
        for filename in self.SPECIAL_FILENAMES:
            parent = 'My Files/Documents'
            path = f'{parent}/{filename}'
            new_name = 'renamed.txt'
            self._init_services(execute_response=self._task_reference)
            self._services.files.rename(path, new_name, wait=False)
            self._services.api.execute.assert_called_once_with('', 'moveResources', mock.ANY)
            actual_param = self._services.api.execute.call_args[0][2]
            self.assertEqual(actual_param.urls[0].src, self._expected_encoded_absolute(path),
                             f'rename() did not encode source for filename: {filename}')
            expected_dest = self._expected_encoded_absolute(f'{parent}/{new_name}')
            self.assertEqual(actual_param.urls[0].dest, expected_dest,
                             f'rename() did not encode dest for filename: {filename}')

    def test_rename_to_special_char_name(self):
        parent = 'My Files/Documents'
        path = f'{parent}/document.txt'
        for new_name in self.SPECIAL_FILENAMES:
            self._init_services(execute_response=self._task_reference)
            self._services.files.rename(path, new_name, wait=False)
            actual_param = self._services.api.execute.call_args[0][2]
            expected_dest = self._expected_encoded_absolute(f'{parent}/{new_name}')
            self.assertEqual(actual_param.urls[0].dest, expected_dest,
                             f'rename() did not encode dest for new name: {new_name}')

    def test_rename_special_char_in_directory(self):
        parent = 'My Files/100% Complete'
        old_name = 'document.txt'
        new_name = 'renamed.txt'
        path = f'{parent}/{old_name}'
        self._init_services(execute_response=self._task_reference)
        self._services.files.rename(path, new_name, wait=False)
        actual_param = self._services.api.execute.call_args[0][2]
        self.assertEqual(actual_param.urls[0].src, self._expected_encoded_absolute(path))
        self.assertEqual(actual_param.urls[0].dest, self._expected_encoded_absolute(f'{parent}/{new_name}'))

    def test_rename_percent_to_percent(self):
        parent = 'My Files'
        old_name = 'file_100%_done.txt'
        new_name = 'file_50%_done.txt'
        path = f'{parent}/{old_name}'
        self._init_services(execute_response=self._task_reference)
        self._services.files.rename(path, new_name, wait=False)
        actual_param = self._services.api.execute.call_args[0][2]
        self.assertEqual(actual_param.urls[0].src, self._expected_encoded_absolute(path))
        self.assertEqual(actual_param.urls[0].dest, self._expected_encoded_absolute(f'{parent}/{new_name}'))

    # --- ListVersions ---

    def test_versions_encodes_special_characters(self):
        for filename in self.SPECIAL_FILENAMES:
            path = f'My Files/{filename}'
            self._init_services(execute_response=[self._create_snapshot_response(path)])
            self._services.files.versions(path)
            self._services.api.execute.assert_called_once_with(
                '', 'listSnapshots', self._expected_encoded_absolute(path)
            )

    def test_versions_percent_in_directory(self):
        path = 'My Files/100% Complete/document.txt'
        self._init_services(execute_response=[self._create_snapshot_response(path)])
        self._services.files.versions(path)
        self._services.api.execute.assert_called_once_with(
            '', 'listSnapshots', self._expected_encoded_absolute(path)
        )

    # --- ListDir ---

    def test_listdir_encodes_special_characters(self):
        self.patch_call("cterasdk.cio.core.commands.EnsureDirectory.execute")
        for directory in self.SPECIAL_DIRECTORIES:
            self._init_services(execute_response=Object(**{
                'errorType': None,
                'hasMore': False,
                'items': []
            }))
            list(self._services.files.listdir(directory))
            actual_param = self._services.api.execute.call_args[0][2]
            self.assertEqual(actual_param.root, self._expected_encoded_absolute(directory),
                             f'listdir() did not encode path for directory: {directory}')

    # --- Mkdir ---

    def test_mkdir_encodes_special_characters(self):
        for directory in self.SPECIAL_DIRECTORIES:
            self._init_services()
            self._services.files.mkdir(directory)
            actual_param = self._services.api.execute.call_args[0][2]
            parts = directory.split('/')
            parent = '/'.join(parts[:-1])
            expected_parent = f'{self._base}/{quote(parent)}'
            self.assertEqual(actual_param.parentPath, expected_parent,
                             f'mkdir() did not encode parentPath for directory: {directory}')

    # --- Helpers ---

    def _create_snapshot_response(self, path):
        return munch.Munch({
            'url': self._base,
            'path': path,
            'current': True,
            'startTimestamp': datetime.now().isoformat(),
            'calculatedTimestamp': datetime.now().isoformat()
        })
