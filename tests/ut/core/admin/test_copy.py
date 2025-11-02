from unittest import mock
from pathlib import Path

from cterasdk.common.object import Object
from cterasdk.cio.core import CorePath
from tests.ut.core.admin import base_admin


class TestCoreFilesBrowser(base_admin.BaseCoreTest):
    _base_path = '/admin/webdav'
    _task_reference = 'servers/MainDB/bgTasks/918908'

    def test_copy_no_wait(self):
        expected_response = TestCoreFilesBrowser._task_reference
        src = 'path/to/file'
        dst = 'destination/folder/path'
        self._init_global_admin(execute_response=expected_response)
        actual_response = self._global_admin.files.copy(src, destination=dst, wait=False)
        self.assertEqual(expected_response, actual_response)
        self._global_admin.api.execute.assert_called_once_with('', 'copyResources', mock.ANY)
        expected_copy_param = self._get_expected_copy_params(src, dst)
        actual_copy_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_copy_param, expected_copy_param)

    def _get_expected_copy_params(self, src, dst):
        o = Object()
        o._classname = 'ActionResourcesParam'  # pylint: disable=protected-access
        o.startFrom = None
        src_dst_obj = Object()
        src_dst_obj._classname = 'SrcDstParam'  # pylint: disable=protected-access
        src_path = self._get_object_path(src).absolute
        src_dst_obj.src = src_path.absolute
        src_dst_obj.dest = self._get_object_path(dst).join(src.name).absolute
        o.urls = [src_dst_obj]
        return o

    def _get_object_path(self, path):
        return CorePath(self._base_path, path)
