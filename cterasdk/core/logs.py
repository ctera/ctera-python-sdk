from datetime import datetime

from .base_command import BaseCommand
from ..lib import Iterator, Command
from ..core import enum
from . import query


class Logs(BaseCommand):
    """
    Portal Logs APIs
    """

    def get(self, topic=enum.LogTopic.System, minSeverity=enum.Severity.INFO, originType=enum.OriginType.Portal, before=None, after=None):
        """
        Get logs from the Portal

        :param cterasdk.core.enum.LogTopic,optional topic: Log topic to get, defaults to cterasdk.core.enum.LogTopic.System
        :param cterasdk.core.enum.Severity,optional minSeverity:
         Minimun severity of logs to get, defaults to cterasdk.core.enum.Severity.INFO
        :param cterasdk.core.enum.OriginType,optional originType:
         Origin type of the logs to get, defaults to cterasdk.core.enum.OriginType.Portal
        :param str,optional before: Get logs before this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param str,optional after: Get logs after this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        """
        builder = query.QueryParamBuilder().put('topic', topic).put('minSeverity', minSeverity)

        builder.addFilter(query.FilterBuilder('originType').eq(originType))

        if before is not None:
            builder.addFilter(query.FilterBuilder('time').before(self._strptime(before)))

        if after is not None:
            builder.addFilter(query.FilterBuilder('time').after(self._strptime(after)))

        param = builder.build()
        function = Command(self._query_logs)

        return Iterator(function, param)

    def _query_logs(self, param):
        response = self._portal.execute('', 'queryLogs', param)
        return (response.hasMore, response.logs)

    @staticmethod
    def _strptime(datetime_str):
        try:
            return datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
        except ValueError as error:
            raise error
