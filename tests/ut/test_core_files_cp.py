import os
from unittest import mock

from cterasdk.common.object import Object
from cterasdk.core.files import cp
from cterasdk.core.files.path import CTERAPath
from tests.ut import base_core


class TestCoreFilesBrowser(base_core.BaseCoreTest):
    _base_path = '/admin/webdav/Users'

    def test_copy(self):
        expected_response = 'success'
        src = 'cloud/Users'
        dst = 'public'
        self._init_global_admin(execute_response=expected_response)
        actual_response = cp.copy(self._global_admin, self._mkpath(src), self._mkpath(dst))
        self.assertEqual(expected_response, actual_response)
        self._global_admin.execute.assert_called_once_with('', 'copyResources', mock.ANY)
        expected_copy_param = self._get_expected_copy_params(src, dst)
        actual_copy_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_copy_param, expected_copy_param)

    def _get_expected_copy_params(self, src, dst):
        o = Object()
        o._classname = 'ActionResourcesParam'  # pylint: disable=protected-access
        src_dst_obj = Object()
        src_dst_obj._classname = 'SrcDstParam'  # pylint: disable=protected-access
        src_path = self._mkpath(src)
        src_dst_obj.src = src_path.fullpath()
        src_dst_obj.dest = os.path.join(self._mkpath(dst).fullpath(), src_path.name())
        o.urls = [src_dst_obj]
        return o

    def _mkpath(self, path):
        return CTERAPath(path, self._base_path)
