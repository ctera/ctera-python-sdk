from unittest import mock
import munch
from cterasdk.asynchronous.core import cloudfs
from cterasdk.core.query import QueryParamBuilder, FilterBuilder
from tests.ut.aio import base_core


class TestAsyncCoreUsers(base_core.BaseAsyncCoreTest):

    def setUp(self):
        super().setUp()
        self._user_id = 56
        self._name = 'My Files'
        self._owner = 'owner'

    async def test_find(self):
        self._global_admin.users.get = mock.AsyncMock(return_value=munch.Munch({'uid': self._user_id}))
        builder = QueryParamBuilder().include(cloudfs.CloudDrives.default).ownedBy(self._user_id)
        builder.addFilter(FilterBuilder('name').eq(self._name))
        expected_param = builder.build()
        with mock.patch("cterasdk.asynchronous.core.cloudfs.query.iterator") as query_iterator_mock:
            await cloudfs.CloudDrives(self._global_admin).find(self._name, self._owner)
        self._global_admin.users.get.assert_called_once_with(self._owner, ['uid'])
        query_iterator_mock.assert_called_once_with(self._global_admin, '/cloudDrives', mock.ANY)
        self.assert_equal_objects(query_iterator_mock.call_args[0][2], expected_param)

        
        