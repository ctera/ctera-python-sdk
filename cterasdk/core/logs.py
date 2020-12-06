from datetime import datetime

from .base_command import BaseCommand
from ..lib import Iterator, Command
from ..core import enum
from . import query


class Logs(BaseCommand):
    """
    Portal Logs APIs
    """

    def device(self,
               name,
               topic=enum.LogTopic.System,
               min_severity=enum.Severity.INFO,
               before=None,
               after=None,
               filters=None):
        """
        Get device logs from the Portal

        :param str name: Name of a device
        :param cterasdk.core.enum.LogTopic,optional topic: Log topic to get, defaults to cterasdk.core.enum.LogTopic.System
        :param cterasdk.core.enum.Severity,optional min_severity:
         Minimun severity of logs to get, defaults to cterasdk.core.enum.Severity.INFO
        :param str,optional before: Get logs before this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param str,optional after: Get logs after this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param list[cterasdk.core.query.FilterBuilder],optional filters: List of additional filters, defaults to None

        :return: Iterator for all matching logs
        :rtype: cterasdk.lib.iterator.Iterator[cterasdk.object.Object]
        """
        return self.get(topic, min_severity, enum.OriginType.Device, name, before, after, filters)

    def get(self, topic=enum.LogTopic.System, min_severity=enum.Severity.INFO, origin_type=enum.OriginType.Portal, origin=None,
            before=None, after=None, filters=None):
        """
        Get logs from the Portal

        :param cterasdk.core.enum.LogTopic,optional topic: Log topic to get, defaults to cterasdk.core.enum.LogTopic.System
        :param cterasdk.core.enum.Severity,optional min_severity:
         Minimun severity of logs to get, defaults to cterasdk.core.enum.Severity.INFO
        :param cterasdk.core.enum.OriginType,optional origin_type:
         Origin type of the logs to get, defaults to cterasdk.core.enum.OriginType.Portal
        :param str,optional origin: Log origin (e.g. device name, Portal server name), defaults to None
        :param str,optional before: Get logs before this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param str,optional after: Get logs after this date (in format "%m/%d/%Y %H:%M:%S"), defaults to None
        :param list[cterasdk.core.query.FilterBuilder],optional filters: List of additional filters, defaults to None

        :return: Iterator for all matching logs
        :rtype: cterasdk.lib.iterator.Iterator[cterasdk.object.Object]
        """
        builder = query.QueryParamBuilder().put('topic', topic).put('minSeverity', min_severity)

        builder.addFilter(query.FilterBuilder('originType').eq(origin_type))

        if before is not None:
            builder.addFilter(query.FilterBuilder('time').before(self._strptime(before)))

        if after is not None:
            builder.addFilter(query.FilterBuilder('time').after(self._strptime(after)))

        if origin is not None:
            builder.addFilter(query.FilterBuilder.ref('origin').eq(origin))

        if filters:
            for user_filter in filters:
                builder.addFilter(user_filter)

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
