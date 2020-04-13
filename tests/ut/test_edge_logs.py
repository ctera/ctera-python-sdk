from unittest import mock

from cterasdk.edge import logs
from cterasdk.edge.enum import Severity
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeLogs(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._topic = 'topic'

    def test_get_logs_default_attrs(self):
        error_logs = ['log-' + str(i) for i in range(6)]
        execute_response = TestEdgeLogs._get_query_logs_response(False, error_logs)
        self._init_filer(execute_response=execute_response)
        error_log_iterator = logs.Logs(self._filer).logs(self._topic, minSeverity=Severity.ERROR)
        for actual_log in error_log_iterator:
            expected_log = error_logs.pop(0)
            self.assertEqual(expected_log, actual_log)
        self._filer.execute.assert_called_once_with('/config/logging/general', 'pagedQuery', mock.ANY)

    @staticmethod
    def _get_query_logs_response(has_more, log_events):
        response = Object()
        response.hasMore = has_more
        response.logs = list(log_events)
        return response
