from unittest import mock
import munch

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
