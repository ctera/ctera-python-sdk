from unittest import mock
import munch

from cterasdk.common import Object
from cterasdk import exceptions

from tests.ut.core.user import base_user


class BaseCoreServicesFilesMkdir(base_user.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._directory = 'documents'
        self._directories = 'the/quick/brown/fox/jumped/over/the/lazy/dog'

    def test_mkdir(self):
        self._init_services()
        self._services.files.mkdir(self._directory)
        self._services.api.execute.assert_called_once_with('', 'makeCollection', mock.ANY)
        expected_param = munch.Munch({
            'name': self._directory,
            'parentPath': f'{self._base}'
        })
        actual_param = self._services.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_mkdir_strict_permission_success(self):
        self._init_services(execute_response=None)
        ret = self._services.files.mkdir(self._directory, strict_permission=True)
        self.assertEqual(ret, self._directory)

    def test_mkdir_strict_permission_denied(self):
        execute_response = Object(rc=0)
        self._init_services(execute_response=execute_response)
        with self.assertRaises(exceptions.io.core.PrivilegeError):
            self._services.files.mkdir(self._directory, strict_permission=True)

    def test_mkdir_strict_permission_denied_message(self):
        execute_response = Object(msg='access denied')
        self._init_services(execute_response=execute_response)
        with self.assertRaises(exceptions.io.core.PrivilegeError):
            self._services.files.mkdir(self._directory, strict_permission=True)

    def test_makedirs_strict_permission_root_path(self):
        rooted_directories = 'Team Portal/Engineering/Documents'
        self._init_services(execute_response=None)
        ret = self._services.files.makedirs(rooted_directories, strict_permission=True)
        self.assertEqual(self._services.api.execute.call_count, len(rooted_directories.split('/')))
        self.assertEqual(ret, rooted_directories)
