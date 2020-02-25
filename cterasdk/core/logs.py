from datetime import datetime

from .base_command import BaseCommand
from ..lib import Iterator, Command
from ..core import enum
from . import query


class Logs(BaseCommand):

    def logs(self, topic=enum.LogTopic.System, minSeverity=enum.Severity.INFO, _originType=enum.OriginType.Portal, before=None, after=None):
        builder = query.QueryParamBuilder().put('topic', topic).put('minSeverity', minSeverity)

        if before is not None:
            builder.addFilter(query.FilterBuilder('time').before(self.strptime(before)))

        if after is not None:
            builder.addFilter(query.FilterBuilder('time').after(self.strptime(after)))

        param = builder.build()
        function = Command(self._query_logs)

        return Iterator(function, param)

    def _query_logs(self, param):
        response = self._portal.execute('', 'queryLogs', param)
        return (response.hasMore, response.logs)

    @staticmethod
    def strptime(datetime_str):
        try:
            return datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
        except ValueError as error:
            raise error
