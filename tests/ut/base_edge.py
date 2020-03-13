import unittest.mock as mock

from cterasdk.object import Gateway
from tests.ut import base


class BaseEdgeTest(base.BaseTest):

    def setUp(self):
        super().setUp()
        self._filer = Gateway("")

    def _init_filer(self, get_response=None, put_response=None, post_response=None,
                    add_response=None, execute_response=None, delete_response=None):
        self._filer.get = mock.MagicMock(return_value=get_response)
        self._filer.put = mock.MagicMock(return_value=put_response)
        self._filer.post = mock.MagicMock(return_value=post_response)
        self._filer.add = mock.MagicMock(return_value=add_response)
        self._filer.execute = mock.MagicMock(return_value=execute_response)
        self._filer.delete = mock.MagicMock(return_value=delete_response)
