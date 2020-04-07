from datetime import date, timedelta

from cterasdk.common import Object
from cterasdk.core.enum import LogTopic, Severity, OriginType
from cterasdk.core import query
from cterasdk.core import logs
from tests.ut import base_core


class TestCoreLogs(base_core.BaseCoreTest):

    def test_get_logs_default_args(self):
        self._init_global_admin(execute_response=self._get_empty_log_response())
        logs_iterator = logs.Logs(self._global_admin).get()
        for log in logs_iterator:
            print(log)
        origin_type_filter = base_core.BaseCoreTest._create_filter(query.FilterType.String, 'originType',
                                                                   query.Restriction.EQUALS, OriginType.Portal)
        expected_query_params = base_core.BaseCoreTest._create_query_params(filters=[origin_type_filter],
                                                                            start_from=0, count_limit=50, topic=LogTopic.System,
                                                                            minSeverity=Severity.INFO)
        actual_query_params = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_get_error_logs_from_yesterday(self):
        self._init_global_admin(execute_response=self._get_empty_log_response())
        yesterday = date.today() - timedelta(days=1)
        before = TestCoreLogs.format_input_date(yesterday, '23:59:59')
        after = TestCoreLogs.format_input_date(yesterday, '00:00:00')
        logs_iterator = logs.Logs(self._global_admin).get(minSeverity=Severity.ERROR, before=before, after=after)
        for log in logs_iterator:
            print(log)
        origin_type_filter = base_core.BaseCoreTest._create_filter(query.FilterType.String, 'originType',
                                                                   query.Restriction.EQUALS, OriginType.Portal)
        before_t_time = TestCoreLogs.format_t_time(yesterday, '23:59:59')
        before_filter = base_core.BaseCoreTest._create_filter(query.FilterType.DateTime, 'time',
                                                              query.Restriction.LESS_THAN, before_t_time)
        after_t_time = TestCoreLogs.format_t_time(yesterday, '00:00:00')
        after_filter = base_core.BaseCoreTest._create_filter(query.FilterType.DateTime, 'time',
                                                             query.Restriction.GREATER_THAN, after_t_time)
        expected_query_params = base_core.BaseCoreTest._create_query_params(filters=[origin_type_filter, before_filter, after_filter],
                                                                            start_from=0, count_limit=50, topic=LogTopic.System,
                                                                            minSeverity=Severity.ERROR)
        actual_query_params = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_query_params, expected_query_params)

    @staticmethod
    def format_input_date(date_object, time):
        return date_object.strftime("%m/%d/%Y") + ' ' + time

    @staticmethod
    def format_t_time(date_object, time):
        return date_object.strftime("%Y-%m-%d") + 'T' + time

    @staticmethod
    def _get_empty_log_response():
        response = Object()
        response.hasMore = False
        response.logs = []
        return response
