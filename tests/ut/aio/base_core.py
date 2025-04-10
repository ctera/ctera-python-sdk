from unittest import mock

from cterasdk.objects import AsyncGlobalAdmin
from tests.ut.aio import base


class BaseAsyncCoreTest(base.BaseAsyncTest):

    def setUp(self):
        super().setUp()
        self._global_admin = AsyncGlobalAdmin("")

    def _init_global_admin(self, get_multi_response=None, form_data_response=None, post_response=None):
        self._global_admin.v1.api.get_multi = mock.AsyncMock(return_value=get_multi_response)
        self._global_admin.v1.api.form_data = mock.AsyncMock(return_value=form_data_response)
        self._global_admin.v2.api.post = mock.AsyncMock(return_value=post_response)
