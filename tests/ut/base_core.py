import unittest.mock as mock

from cterasdk.object import GlobalAdmin
from tests.ut import base


class BaseCoreTest(base.BaseTest):

    def setUp(self):
        super().setUp()
        self._global_admin = GlobalAdmin("")

    def _init_global_admin(self, get_response=None, get_multi_response=None, execute_response=None, delete_response=None):
        self._global_admin.get = mock.MagicMock(return_value=get_response)
        self._global_admin.get_multi = mock.MagicMock(return_value=get_multi_response)
        self._global_admin.execute = mock.MagicMock(return_value=execute_response)
        self._global_admin.delete = mock.MagicMock(return_value=delete_response)
