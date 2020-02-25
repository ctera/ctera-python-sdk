from ..lib import Command, Iterator
from . import query
from . import enum
from .base_command import BaseCommand


class Logs(BaseCommand):
    default_include = ['severity', 'time', 'msg', 'more']

    def logs(self, topic, include=None, minSeverity=enum.Severity.INFO):
        param = query.QueryParamBuilder().include(
            include or Logs.default_include).put('topic', topic).put('minSeverity', minSeverity).build()
        function = Command(self._query_logs)
        return Iterator(function, param)

    def _query_logs(self, param):
        response = self._gateway.execute('/config/logging/general', 'pagedQuery', param)
        return (response.hasMore, response.logs)
