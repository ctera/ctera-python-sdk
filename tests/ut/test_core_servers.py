# pylint: disable=protected-access
from unittest import mock

from cterasdk.core import servers
from tests.ut import base_core


class TestCoreServers(base_core.BaseCoreTest):

    def test_list_servers_default_attrs(self):
        with mock.patch("cterasdk.core.servers.query.iterator") as query_iterator_mock:
            servers.Servers(self._global_admin).list_servers()
            query_iterator_mock.assert_called_once_with(self._global_admin, '/servers', mock.ANY)
            expected_query_params = base_core.BaseCoreTest._create_query_params(include=servers.Servers.default,
                                                                                start_from=0, count_limit=50)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)
