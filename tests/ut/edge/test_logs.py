from unittest import mock

from cterasdk.edge import logs
from cterasdk.edge.enum import Severity
from cterasdk.common import Object
from tests.ut.edge import base_edge


class TestEdgeLogs(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._topic = 'topic'
        self._days = 30

    def test_get_logs_default_attrs(self):
        error_logs = ['log-' + str(i) for i in range(6)]
        execute_response = TestEdgeLogs._get_query_logs_response(False, error_logs)
        self._init_filer(execute_response=execute_response)
        error_log_iterator = logs.Logs(self._filer).logs(self._topic, minSeverity=Severity.ERROR)
        for actual_log in error_log_iterator:
            expected_log = error_logs.pop(0)
            self.assertEqual(expected_log, actual_log)
        self._filer.api.execute.assert_called_once_with('/config/logging/general', 'pagedQuery', mock.ANY)

    def test_modify_log_settings(self):
        get_response = TestEdgeLogs._get_log_settings(7, Severity.INFO)
        self._init_filer(get_response=get_response)
        logs.Logs(self._filer).settings(self._days, min_severity=Severity.CRITICAL)
        self._filer.api.get.assert_called_once_with('/config/logging/general')
        self._filer.api.put.assert_called_once_with('/config/logging/general', mock.ANY)
        expected_param = TestEdgeLogs._get_log_settings(self._days, Severity.CRITICAL)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_log_settings(log_keep_period, min_severity):
        param = Object()
        param.LogKeepPeriod = log_keep_period
        param.minSeverity = min_severity
        return param

    @staticmethod
    def _get_query_logs_response(has_more, log_events):
        response = Object()
        response.hasMore = has_more
        response.logs = list(log_events)
        return response
